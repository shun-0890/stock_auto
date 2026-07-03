#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
52銘柄のスクリーニング用データ取得スクリプト
日本の株式情報サイトから情報を取得して、JSON形式で出力
"""

import json
import requests
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
import time
from urllib.parse import quote

# スクレイピング用のユーザーエージェント
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

SCREENING_DATE = '2026-07-03'

def read_watchlist(filepath: str) -> List[Dict[str, str]]:
    """CSVからwatchlistを読み込む"""
    stocks = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[1:]:  # ヘッダー行をスキップ
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    stocks.append({
                        'code': parts[0],
                        'name': parts[1],
                        'market': parts[2]
                    })
    except Exception as e:
        print(f"Error reading watchlist: {e}", file=sys.stderr)
        return []

    return stocks

def fetch_yahoo_stock_data(code: str) -> Dict[str, Any]:
    """Yahoo Finance JPから株式情報をスクレイピング"""
    try:
        url = f'https://finance.yahoo.co.jp/quote/{code}.T'
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'

        data = {
            'current_price': 0,
            'market_cap_billion': 0,
            '52week_high_price': 0,
            '52week_high_date': None,
            'price_rise_from_high_pct': 0,
            'volume': None,
        }

        # 正規表現で主要な情報を抽出
        # 現在株価
        price_match = re.search(r'現在値[\":\s]+([\d,\.]+)', response.text)
        if price_match:
            try:
                price_str = price_match.group(1).replace(',', '')
                data['current_price'] = float(price_str)
            except:
                pass

        # 52週高値
        high52w_match = re.search(r'52週高値[\":\s]+([\d,\.]+)', response.text)
        if high52w_match:
            try:
                high_str = high52w_match.group(1).replace(',', '')
                data['52week_high_price'] = float(high_str)
            except:
                pass

        # 時価総額（複数の形式に対応）
        market_cap_match = re.search(r'時価総額[\":\s]*([0-9.]+)\s*(?:億|百万|兆)?', response.text)
        if market_cap_match:
            try:
                cap_str = market_cap_match.group(1)
                data['market_cap_billion'] = float(cap_str)
            except:
                pass

        return data
    except Exception as e:
        print(f"Error fetching Yahoo data for {code}: {e}", file=sys.stderr)
        return {}

def fetch_stock_search_data(code: str, name: str) -> Dict[str, Any]:
    """ウェブ検索で銘柄の詳細情報を取得"""
    try:
        # 株探などの情報サイトから検索
        search_url = f'https://www.kabutan.jp/stock/chart?code={code}'
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'

        data = {
            'business_model': '確認中',
            'unique_tech': False,
            'growth_market': '該当なし',
            'financial_status': '不明',
            'price_rise_factor': '不明',
            'mass_production_order': '不明',
        }

        # ページから情報を抽出
        if '医療' in response.text or 'AI' in response.text:
            data['growth_market'] = 'AI/医療'

        return data
    except Exception as e:
        print(f"Error fetching search data for {code}: {e}", file=sys.stderr)
        return {}

def estimate_screening_values(stock: Dict[str, str], yahoo_data: Dict[str, Any]) -> Dict[str, Any]:
    """取得したデータからスクリーニング値を推定"""

    market = 'グロース' if 'グロース' in stock['market'] else 'スタンダード'

    current_price = yahoo_data.get('current_price', 0)
    high52w_price = yahoo_data.get('52week_high_price', 0)

    # 52週高値からの上昇率を計算
    price_rise_pct = 0
    if high52w_price > 0 and current_price > 0:
        price_rise_pct = ((current_price - high52w_price) / high52w_price) * 100

    # テンバガー候補の判定（概算）
    is_breakout_initial = False
    if 0 < price_rise_pct < 40:  # ブレイク初動の可能性
        is_breakout_initial = True

    screening_data = {
        'code': stock['code'],
        'name': stock['name'],
        'market': market,
        'current_price': current_price,
        'market_cap_billion': yahoo_data.get('market_cap_billion', 0),
        '52week_high_date': yahoo_data.get('52week_high_date', SCREENING_DATE),
        '52week_high_price': high52w_price,
        'price_rise_from_high_pct': round(price_rise_pct, 2),
        'days_since_52week_high': 0,  # 正確な日付がないため0で設定
        'is_breakout_initial': is_breakout_initial,
        'breakout_rise_pct': max(0, price_rise_pct),
        'volume_status': '不明',  # 詳細調査が必要
        'financial_status': '不明',
        'price_rise_factor': '要確認',
        'is_onetime_material': False,
        'business_model': '確認中',
        'unique_tech': False,
        'growth_market': '不明',
        'mass_production_order': '不明',
        'operating_margin_trend': '不明',
        'notes': 'ウェブスクレイピングで取得した基本情報。詳細は個別調査が必要。'
    }

    return screening_data

def create_screening_json(stocks: List[Dict[str, str]]) -> Dict[str, Any]:
    """スクリーニングデータをJSON形式で作成"""

    screening_data = {
        'screening_date': SCREENING_DATE,
        'stocks': []
    }

    total = len(stocks)
    for i, stock in enumerate(stocks, 1):
        code = stock['code']
        name = stock['name']

        print(f"[{i:2d}/{total}] Fetching: {code} {name}", file=sys.stderr)

        # Yahoo Finance JPから基本データを取得
        yahoo_data = fetch_yahoo_stock_data(code)

        # 追加情報を取得（必要に応じて）
        extra_data = fetch_stock_search_data(code, name)

        # スクリーニング値を構築
        stock_screening = estimate_screening_values(stock, yahoo_data)
        stock_screening.update(extra_data)

        screening_data['stocks'].append(stock_screening)

        # レート制限を回避するため短い待機
        time.sleep(1)

    return screening_data

def main():
    """メイン処理"""
    try:
        watchlist_file = '/home/user/stock_auto/targets/2026-07-03_watchlist.csv'

        # Watchlistを読み込む
        stocks = read_watchlist(watchlist_file)
        if not stocks:
            print("No stocks found in watchlist", file=sys.stderr)
            sys.exit(1)

        print(f"Loaded {len(stocks)} stocks from watchlist", file=sys.stderr)

        # スクリーニングデータを作成
        screening_data = create_screening_json(stocks)

        # JSONを標準出力に出力
        print(json.dumps(screening_data, ensure_ascii=False, indent=2))

    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
