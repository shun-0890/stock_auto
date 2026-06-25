# マクロ分析データ収集ガイド

## 概要

本ドキュメントは、日本時間の営業日終場後（日本時間15:00-16:00以降）に、翌日のマクロ分析に必要なデータ収集方法を指示します。

**ネットワーク制限対応**: 本プロジェクトの実行環境では一部の金融データサイトへのアクセスが制限されているため、以下の手段でのデータ取得を推奨します：

1. **推奨**: ユーザー自身がブラウザで各サイトを訪問し、値を記録
2. **代替案**: 別環境（個人PCなど）でスクリプトを実行してCSVで取得
3. **実運用**: セキュリティポリシー許可後にAPIキー経由での自動取得

---

## 1. 米国市場データ

### ソース: Yahoo Finance / Bloomberg / CNBC Markets

| 指数 | ティッカー | 確認項目 | URL例 |
|------|-----------|---------|-------|
| NYダウ | ^DJI | 終値、前日比（ドル・％）、前週比 | https://finance.yahoo.com/quote/%5EDJI/ |
| S&P500 | ^GSPC | 終値、前日比、前週比 | https://finance.yahoo.com/quote/%5EGSPC/ |
| NASDAQ | ^IXIC | 終値、前日比、前週比 | https://finance.yahoo.com/quote/%5EIXIC/ |
| Russell2000 | ^RUT | 終値、前日比 | https://finance.yahoo.com/quote/%5ERUT/ |
| SOX（半導体） | ^SOX | 終値、前日比、前週比 | https://finance.yahoo.com/quote/%5ESOX/ |
| VIX（恐怖指数） | ^VIX | 現在値、前日比 | https://finance.yahoo.com/quote/%5EVIX/ |

### 入力先

`data/macro_data_template.json` の以下フィールド：
```json
"us_market": {
  "dow_jones": { "closing_value": 49000, "change_from_previous_day": 150, "change_percentage": 0.31 },
  "sp500": { "closing_value": 7400 },
  ...
}
```

---

## 2. 日本市場データ

### ソース: 日本経済新聞 / 株式新聞 / Yahoo Finance Japan

| 指数 | ティッカー | 確認項目 | URL例 |
|------|-----------|---------|-------|
| 日経平均 | 0225.SA / ^N225 | 終値、前日比、高値、安値 | https://nikkei.com/markets/index/ または https://finance.yahoo.com/quote/0225.SA/ |
| TOPIX | ^TOPIX | 終値、前日比 | https://finance.yahoo.com/quote/%5ETPX/ |
| グロース250 | Growth250 | 終値、前日比 | 日経Web または Bloomberg |
| 東証プライム売買代金 | - | 当日売買代金（概算兆円）、騰落銘柄数 | 日経新聞 / 株式新聞Web |
| グロース市場売買代金 | - | 当日売買代金（概算）、騰落銘柄数 | 株式新聞Web |

### 入力先

```json
"japan_market": {
  "nikkei225": { "closing_value": 60500, "change_from_previous_day": -250 },
  "prime_market": { "trading_volume": 4.2, "advancing_stocks": 1500, "declining_stocks": 800 },
  ...
}
```

---

## 3. 為替・コモディティ

### ソース: Yahoo Finance / Trading Economics / Investing.com

| 項目 | ティッカー | 単位 | 確認項目 |
|------|-----------|------|---------|
| USD/JPY | JPYUSD=X | JPY | 現在値、前日比、方向感 |
| EUR/JPY | EURJPY=X | JPY | 現在値、前日比 |
| EUR/USD | EURUSD=X | USD | 現在値、前日比 |
| WTI原油 | CL=F | USD/bbl | 現在値、前日比 |
| ブレント原油 | BZ=F | USD/bbl | 現在値、前日比 |
| ゴールド | GC=F | USD/oz | 現在値、前日比 |
| 銅 | HG=F | USD/lb | 現在値、前日比 |
| 天然ガス（オプション） | NG=F | USD/MMBtu | 現在値 |

### 特記事項

- **ドル円**: 160円接近で日本財務省の介入警戒が高まる水準
- **原油**: ホルムズ海峡リスク（イラン・中東情勢）を反映
- **ゴールド**: インフレヘッジ・リスク回避需要が買い要因
- **銅**: 中国景気・グリーン転換需要に連動

### 入力先

```json
"forex_commodities": {
  "usd_jpy": { "level": 159.5, "change": 0.5 },
  "wti_oil": { "level": 107.35, "change": 0.5 },
  ...
}
```

---

## 4. 金利・債券

### ソース: Yahoo Finance / Trading Economics / Federal Reserve

| 指標 | ティッカー / ソース | 単位 | 確認項目 |
|------|-------------------|------|---------|
| 米10年国債利回り | ^TNX | % | 現在値、前日比、高値・安値 |
| 米2年国債利回り | ^TYX | % | 現在値 |
| 日本10年国債利回り | JGB10Y（各金融サイト） | % | 現在値、前日比 |
| 米10年−2年スプレッド | 計算値（10Y - 2Y） | % | 逆イールド状態の判定 |

### 逆イールド判定

- **正常状態**: 10年 > 2年（スプレッド +0.5% 以上）
- **逆イールド**: 10年 < 2年（スプレッド マイナス）
- **フラット**: 10年 ≈ 2年

### 入力先

```json
"interest_rates": {
  "us_10y_yield": { "level": 4.6, "change_basis_points": 8 },
  "japan_10y_yield": { "level": 2.8, "change_basis_points": 10 },
  ...
}
```

---

## 5. 中央銀行・政策動向

### FRB（米連邦準備制度理事会）

**ソース**: Federal Reserve 公式サイト / CNBC / CME FedWatch

確認項目：
- 政策金利（現行レンジ）: 例）4.75-5.00%
- 次回利下げ予想: 例）「2027年中頃」
- 政策トーン: タカ派 / ハト派 / ニュートラル
- 主要懸念点: インフレ、スタグフレーションリスク等

**CME FedWatch**での利下げ確率確認：
- https://www.cmegroup.com/markets/global-market-index/governance.federal-reserve.html

### 日本銀行（BOJ）

**ソース**: 日銀公式サイト / 日経平均新聞

確認項目：
- 政策金利: 例）0.75%
- 政策方向性: 引き締め / 据え置き / 緩和
- 追加利上げ観測: 有無と時期
- 為替介入警戒水準: 160円接近の有無

### 入力先

```json
"central_bank_policy": {
  "fed": { "policy_rate": "4.75-5.00%", "policy_tone": "タカ派" },
  "boj": { "policy_rate": 0.75, "policy_direction": "引き締め継続" },
  ...
}
```

---

## 6. インフレ指標

### ソース: BLS（米国労働統計局）/ Trading Economics / 日本経済新聞

| 指標 | 確認項目 | 頻度 | ソース |
|------|---------|------|-------|
| 米CPI（消費者物価指数） | 前月比・前年同月比 | 毎月中旬発表 | https://www.bls.gov/ |
| 米コアCPI | 食料・エネルギー除外 | 毎月中旬発表 | BLS |
| 米PCE（個人消費支出） | 前月比・前年同月比 | 毎月末発表 | BEA（経済分析局） |
| 米コアPCE | ★FRBが重視 | 毎月末発表 | BEA |
| 日本CPI | 前月比・前年同月比 | 毎月下旬発表 | 総務省統計局 |

### 注記

- **直近発表日**: 月初～中旬（CPI）、月末（PCE）
- **2026-06-24時点**: 5月のインフレデータが最新

### 入力先

```json
"inflation_data": {
  "us_cpi": { "latest_value": 2.4, "month": "2026-05", "year_over_year": 2.5 },
  "us_core_pce": { "latest_value": 3.2 },
  ...
}
```

---

## 7. 地政学・リスク要因

### ソース: CNBC / Reuters / Bloomberg / 日経Web

監視対象：

| リスク | 監視項目 | 株式市場への波及経路 |
|--------|---------|-------------------|
| **イラン・中東紛争** | ホルムズ海峡閉鎖リスク、原油高騰 | 原油高 → インフレ高止まり → 利下げ延期 → グロース株圧力 |
| **米中関係** | 首脳会談、貿易交渉、半導体規制 | 半導体・AI・供給チェーン不透明感 → NASDAQ・SOX下圧力 |
| **ロシア・ウクライナ** | 停戦交渉、欧州防衛費 | 防衛関連株への上昇圧力 |
| **米国債・財政** | 長期金利上昇、外国人売却リスク | グロース株・REIT割引率上昇 |
| **日本長期金利** | JGB金利の上昇ペース | グロース株・REIT圧力継続 |

### 入力先

```json
"geopolitical_risks": {
  "iran_middle_east": { 
    "current_status": "ホルムズ海峡ナバル封鎖継続",
    "wave_factor": "★★★★",
    "impact_on_stocks": ["原油高騰", "スタグフレーション"]
  },
  ...
}
```

---

## 8. 市場センチメント

### ソース: Alternative.me / CNBC / TradingView / 各証券会社

| 指標 | 確認項目 | 解釈 |
|------|---------|------|
| **VIX指数** | 現在値 | <15: 過度な安心 / 15-20: 通常 / 20+: リスクオフ |
| **Fear & Greed Index** | 0-100スケール | 0-25: Fear / 50: Neutral / 75-100: Greed |
| **投資家別動向（日本）** | 外国人、個人、機関投資家のポジション | 利益確定売り vs. 新規買い |
| **信用買い残** | 高水準 vs. 低水準 | 高 = リスク / 低 = 堅実 |
| **空売り比率** | セクター別ショート圧力 | グロース・高PER株への圧力が高い |

### URL例

- **Fear & Greed Index**: https://alternative.me/crypto/fear-and-greed-index/
- **VIX**: https://finance.yahoo.com/quote/%5EVIX/

### 入力先

```json
"market_sentiment": {
  "vix_index": { "current_level": 17, "interpretation": "通常水準" },
  "fear_greed_index": { "current_level": 69, "evaluation": "Greed" },
  ...
}
```

---

## 9. テーマ別資金動向

### 監視対象テーマ（日本株を中心）

| テーマ | 強弱判定 | チェック項目 | 主要銘柄例 |
|--------|---------|-----------|----------|
| AI・半導体（米） | 米中関係、SOX指数の推移 | 米中交渉、規制動向 | NVDA, AMD, TSMC |
| AI・半導体（日） | 金利・SOX連動 | 日本装置株の売買代金 | 東京エレクトロン、レーザーテック |
| 防衛・宇宙 | ロシア・ウクライナ動向 | 日本防衛費予算 | 三菱重工、川崎重工、IHI |
| エネルギー | 原油価格、中東リスク | WTI・ブレント、ホルムズ | INPEX、出光、ENEOS |
| 銀行・保険 | 長期金利、利ザヤ | JGB10年利回り | 三菱UFJ、三井住友、東京海上 |
| グロース・中小型 | グロース250、テック株 | 出遅れ修正の有無 | 医療テック、SaaS系 |
| 円安恩恵（輸出） | USD/JPY水準 | ドル円158-161円帯 | トヨタ、ソニー、精密 |
| REIT・不動産 | 長期金利 | JGB10年利回り2.5%超での圧力 | J-REIT全般 |
| フィジカルAI・ロボティクス | 中長期テーマ | 足元の地合い | ファナック、安川電機 |

### 入力先

```json
"key_themes": {
  "themes": [
    {
      "theme": "AI・半導体",
      "region": "米国",
      "strength": "中立→やや弱",
      "background": "米中関係の不透明感、SOXの調整"
    },
    ...
  ]
}
```

---

## 10. 総合判定基準

各マクロ指標をまとめて、以下の視点で総合評価：

| 判定軸 | 選択肢 | 判定基準 |
|--------|--------|---------|
| **リスクオン/オフ** | リスクオン / 中立 / リスクオフ / 二極化 | VIX, F&G, 資金流, セクター分化で判定 |
| **円安/円高局面** | 円安 / 横ばい / 円高 | USD/JPY水準と日米金利差で判定 |
| **金利環境** | 引き締め長期化 / 正常化 / 緩和方向 | 米10Y, 日10Y, スプレッド, 利下げ見通しで判定 |
| **コモディティ環境** | エネルギー高騰 / 軟調 / 横ばい | WTI, ブレント, 金, 銅の相対動向 |
| **有利セクター** | 複数選択 | 地政学・金利・円安の複合判定 |
| **不利セクター** | 複数選択 | 金利高止まり、SOX調整、業績見通しで判定 |

### 入力先

```json
"market_assessment": {
  "risk_on_off": { "assessment": "中立（二極化）", "reasoning": "..." },
  "yen_trend": { "assessment": "円安（159円台）", "level": 159.04 },
  "favorable_sectors": ["防衛", "エネルギー", "銀行・保険"],
  "unfavorable_sectors": ["高PERグロース", "REIT", "不動産"],
  "overall_summary": "..."
}
```

---

## 11. データ入力フロー（推奨）

### 日次運用（営業日終場後）

**時刻**: 日本時間15:30 - 17:00（米国場開場前日本場終場直後 ~ ナイトセッション前）

**手順**:

1. **米国市場** (前営業日終値の場合は日中に随時確認)
   - [ ] NYダウ、S&P500、NASDAQ、Russell2000、SOX、VIX を Yahoo Finance / CNBC から取得
   - [ ] 上記を `data/macro_data_template.json` の `us_market` に入力

2. **日本市場**（本営業日終場）
   - [ ] 日経平均、TOPIX、グロース250、騰落銘柄数を日経Web / 株式新聞から取得
   - [ ] `japan_market` に入力

3. **為替・コモディティ**
   - [ ] USD/JPY, EUR/JPY, WTI, ゴールド, 銅を取得
   - [ ] `forex_commodities` に入力

4. **金利**
   - [ ] 米10Y, 日10Y を取得
   - [ ] `interest_rates` に入力

5. **中央銀行・政策**
   - [ ] FRB / BOJ の最新スタンス・ニュースを確認
   - [ ] `central_bank_policy` に入力

6. **インフレ・地政学・センチメント**
   - [ ] 最新CPI、VIX、Fear & Greed Index を確認
   - [ ] `inflation_data`, `geopolitical_risks`, `market_sentiment` に入力

7. **テーマ別評価**
   - [ ] 各セクターの強弱判定を実施
   - [ ] `key_themes`, `market_assessment` に入力

8. **ファイル保存**
   ```bash
   # JSONファイルを日付付きで保存
   cp data/macro_data_template.json reports/2026-06-24_macro_data.json
   ```

---

## 12. 自動化オプション（将来実装）

### Python スクリプト例（参考）

```python
import requests
import json
from datetime import datetime

def fetch_us_market():
    """Yahoo Finance API from yfinance"""
    import yfinance as yf
    
    indices = {'^DJI': 'dow_jones', '^GSPC': 'sp500', '^IXIC': 'nasdaq'}
    data = {}
    
    for ticker, name in indices.items():
        info = yf.Ticker(ticker).info
        data[name] = {
            'closing_value': info.get('currentPrice'),
            'change_from_previous_day': info.get('regularMarketChange'),
            'change_percentage': info.get('regularMarketChangePercent')
        }
    
    return data

def fetch_jpy_rates():
    """為替データ取得"""
    import yfinance as yf
    usd_jpy = yf.Ticker('JPYUSD=X').info
    return {'level': usd_jpy.get('bid')}

# メイン処理
if __name__ == '__main__':
    macro_data = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'us_market': fetch_us_market(),
        'forex': fetch_jpy_rates(),
        # ... その他のデータ取得処理
    }
    
    with open(f'reports/{macro_data["date"]}_macro_data.json', 'w') as f:
        json.dump(macro_data, f, indent=2, ensure_ascii=False)
```

---

## 13. トラブルシューティング

### Q. Yahoo Finance にアクセスできない場合？
**A.** 別環境（個人PC）での実行、または以下の代替ソース利用：
- Google Finance: https://www.google.com/finance
- MarketWatch: https://www.marketwatch.com
- 日経平均公式: https://nikkei.com/markets/index/

### Q. リアルタイムデータが取得できない場合？
**A.** 日本時間営業日15:00以後に再試行。米国データは、米国営業日終場直後に取得。

### Q. JSONファイルが壊れた場合？
**A.** 以下のコマンドで検証：
```bash
python3 -m json.tool data/macro_data_template.json
```

---

## 14. 参考リンク集

### 米国市場
- Yahoo Finance: https://finance.yahoo.com
- CNBC Markets: https://www.cnbc.com/markets/
- CME FedWatch: https://www.cmegroup.com/markets/federal-reserve

### 日本市場
- 日本経済新聞 マーケット: https://nikkei.com/markets/
- 株式新聞 Web: https://www.kabusin.com
- 東証公式: https://www.jpx.co.jp

### グローバル経済指標
- Trading Economics: https://tradingeconomics.com
- BLS (米国労働統計): https://www.bls.gov
- 総務省統計局: https://www.stat.go.jp

### 政策・中央銀行
- Federal Reserve: https://www.federalreserve.gov
- 日本銀行: https://www.boj.or.jp
- ECB: https://www.ecb.europa.eu

### リスク・センチメント
- Fear & Greed Index: https://alternative.me/crypto/fear-and-greed-index/
- VIX Index: https://www.cboe.com/tradable_products/vix/
- Market Breadth（株価騰落）: TradingView / Yahoo Finance

---

## 15. 更新履歴

| 日付 | 更新内容 |
|------|---------|
| 2026-06-25 | 初版作成。ネットワーク制限対応版テンプレート・ガイド作成 |

---

**このガイドは定期的に更新されます。最新版は常に本ファイルを参照してください。**
