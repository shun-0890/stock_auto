#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
52銘柄のスクリーニング評価テンプレート作成
環境制限下での基本フレームワーク提供
"""

import json
from datetime import datetime

SCREENING_DATE = '2026-07-03'

# watchlistからCSVを読み込む
watchlist_data = """4596,窪田製薬ホールディングス,東証グロース
3133,海帆,東証グロース
9425,ReYuu Japan,東証スタンダード
6634,J holdings,東証スタンダード
9444,トーシンホールディングス,東証スタンダード
504A,イノバセル,東証グロース
4575,キャンバス,東証グロース
4935,リベルタ,東証スタンダード
4258,網屋,東証グロース
5537,AlbaLink,東証グロース
5133,テリロジーホールディングス,東証スタンダード
5572,Ridge-i,東証グロース
5242,アイズ,東証グロース
4419,Finatextホールディングス,東証グロース
4424,Amazia,東証グロース
4446,Link-Uグループ,東証スタンダード
9553,マイクロアド,東証グロース
4412,サイエンスアーツ,東証グロース
5189,櫻護謨,東証スタンダード
2345,クシム,東証スタンダード
6218,エンシュウ,東証スタンダード
472A,ミラティブ,東証グロース
1447,ITbookホールディングス,東証グロース
2370,メディネット,東証グロース
4667,アイサンテクノロジー,東証スタンダード
5588,ファーストアカウント,東証グロース
2483,翻訳センター,東証スタンダード
2597,ユニカフェ,東証スタンダード
2907,あじかん,東証スタンダード
2999,ホームポジション,東証スタンダード
3131,シンデン・ハイテックス,東証ジャスダック
3184,ICDAホールディングス,東証スタンダード
3418,バルニバービ,東証グロース
4193,ファブリカホールディングス,東証スタンダード
4394,エクスモーション,東証グロース
6037,MART,東証スタンダード
6083,ERIホールディングス,東証スタンダード
6091,ウエスコホールディングス,東証スタンダード
6230,SANEI,東証スタンダード
6316,丸山製作所,東証スタンダード
6334,明治機械,東証スタンダード
6522,アスタリスク,東証グロース
6778,アルチザネットワークス,東証スタンダード
6863,ニレコ,東証スタンダード
7041,CRG HOLDINGS,東証グロース
7069,サイバー・バズ,東証グロース
7417,南陽,東証スタンダード
7505,扶桑電通,東証スタンダード
7523,アールビバン,東証スタンダード
7957,フジコピアン,東証スタンダード
8104,クワザワホールディングス,東証スタンダード
8704,トレイダーズホールディングス,東証スタンダード
8844,コスモスイニシア,東証スタンダード"""

def create_template():
    """スクリーニングテンプレートを作成"""
    
    screening_data = {
        'screening_date': SCREENING_DATE,
        'note': '環境制限により、リアルタイムデータ取得が制限されています。各銘柄について個別の詳細調査が必要です。',
        'stocks': []
    }
    
    for line in watchlist_data.strip().split('\n'):
        parts = line.split(',')
        code = parts[0]
        name = parts[1]
        market_jp = parts[2]
        
        market = 'グロース' if 'グロース' in market_jp else 'スタンダード'
        
        stock_data = {
            'code': code,
            'name': name,
            'market': market,
            'current_price': None,
            'market_cap_billion': None,
            '52week_high_date': None,
            '52week_high_price': None,
            'price_rise_from_high_pct': None,
            'days_since_52week_high': None,
            'is_breakout_initial': None,
            'breakout_rise_pct': None,
            'volume_status': None,
            'financial_status': None,
            'price_rise_factor': None,
            'is_onetime_material': None,
            'business_model': None,
            'unique_tech': None,
            'growth_market': None,
            'mass_production_order': None,
            'operating_margin_trend': None,
            'notes': f'{code} {name} - 詳細調査が必要'
        }
        
        screening_data['stocks'].append(stock_data)
    
    return screening_data

if __name__ == '__main__':
    data = create_template()
    print(json.dumps(data, ensure_ascii=False, indent=2))
