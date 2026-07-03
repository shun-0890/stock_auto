#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
52銘柄のスクリーニング評価データ作成
既存情報と評価レポートを結合
"""

import json

SCREENING_DATE = '2026-07-03'

# 既知の銘柄情報（evaluation.mdから抽出）
KNOWN_STOCKS = {
    '6522': {
        'name': 'アスタリスク',
        'market': 'グロース',
        'business_model': '自社開発LSI「STARプロセッサ」を核としたインテリジェント読み取りデバイスメーカー。ハードウェアに自社チップが搭載されることで、ソフト・ハードの垂直統合モデルへの転換が完了。',
        'unique_tech': True,
        'tech_description': 'STARプロセッサという自社設計LSI。競合のソフトウェアアップデートでは追いつけない処理速度・認識精度の優位性。',
        'growth_market': '工場自動化（スマートファクトリー）・物流DX・スマートリテール',
        'financial_status': '黒字',
        'mass_production_order': '見込みあり',
        'operating_margin_trend': '改善中',
        'notes': '工場DX・物流DX関連。自社LSI搭載で差別化。時価総額96億円。量産案件・利益率の詳細確認が先決。',
        'score': 'B'
    },
    '3446': {
        'name': 'ジェイテックコーポレーション',
        'market': 'グロース',
        'business_model': '研究施設向けシンクロトロン光学素子から、半導体製造・量子フォトニクス向けの産業用精密光学部品への高付加価値シフト。',
        'unique_tech': True,
        'tech_description': 'サブナノメートル精度のX線ミラー製造・計測技術は世界最高水準。SPring-8等の放射光施設向けで世界トップクラス。',
        'growth_market': '半導体製造工程（EUV関連）・量子コンピュータ用フォトニクス',
        'financial_status': '黒字転換見込み',
        'mass_production_order': '受託実績あり',
        'operating_margin_trend': '改善中',
        'notes': '売上49.3%増・利益231.4%増。テンバガー最有力候補。S評価。',
        'score': 'S'
    }
}

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

def create_screening_data():
    """スクリーニングデータを作成"""
    
    screening_data = {
        'screening_date': SCREENING_DATE,
        'metadata': {
            'note': '環境制限により外部データソースへのアクセスが制限されています。既存のプロジェクト評価データから利用可能な情報を統合しています。',
            'data_source': '既存プロジェクト評価レポート＆watchlist',
            'update_status': '一部銘柄の詳細情報は個別ウェブ検索が必要',
            'total_stocks': 52
        },
        'stocks': []
    }
    
    for line in watchlist_data.strip().split('\n'):
        parts = line.split(',')
        code = parts[0]
        name = parts[1]
        market_jp = parts[2]
        
        market = 'グロース' if 'グロース' in market_jp else 'スタンダード'
        
        # 既知の銘柄情報がある場合は使用
        if code in KNOWN_STOCKS:
            known = KNOWN_STOCKS[code]
            stock_data = {
                'code': code,
                'name': known['name'],
                'market': market,
                'current_price': None,  # 要取得
                'market_cap_billion': None,  # 要取得
                '52week_high_date': None,  # 要取得
                '52week_high_price': None,  # 要取得
                'price_rise_from_high_pct': None,  # 要取得
                'days_since_52week_high': None,  # 要取得
                'is_breakout_initial': None,  # 要確認
                'breakout_rise_pct': None,  # 要確認
                'volume_status': None,  # 要取得
                'financial_status': known.get('financial_status', '要確認'),
                'price_rise_factor': None,  # 要確認
                'is_onetime_material': None,  # 要判定
                'business_model': known.get('business_model', '要調査'),
                'unique_tech': known.get('unique_tech', None),
                'growth_market': known.get('growth_market', '要確認'),
                'mass_production_order': known.get('mass_production_order', '要確認'),
                'operating_margin_trend': known.get('operating_margin_trend', '要確認'),
                'evaluation_score': known.get('score', '要評価'),
                'notes': known.get('notes', f'{code} {name} - 既存評価より参照')
            }
        else:
            # 新規銘柄
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
                'evaluation_score': '要調査',
                'notes': f'{code} {name} - 詳細調査が必要。ウェブ検索でのデータ取得推奨。'
            }
        
        screening_data['stocks'].append(stock_data)
    
    return screening_data

if __name__ == '__main__':
    data = create_screening_data()
    print(json.dumps(data, ensure_ascii=False, indent=2))
