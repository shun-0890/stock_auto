# 2026-06-24 マクロ分析データ収集セットアップ完了

## 概要

プロジェクト実行環境のネットワーク制限により、一部の金融データサイトへのアクセスが不可能な状況に対応するため、**マクロ分析データを手動で収集・整理するためのツール一式**を作成しました。

---

## 環境背景

### ネットワーク制限の詳細

本プロジェクトの実行環境では、プロキシポリシーにより以下のサイトへのアクセスが制限されています：

- ❌ Yahoo Finance（query1.finance.yahoo.com）
- ❌ Reuters（www.reuters.com）
- ❌ Federal Reserve（www.federalreserve.gov）
- ❌ その他多くの金融データサイト

**回避策**: ユーザー自身がブラウザで各サイトにアクセスし、必要なデータを手動で記録・入力する環境を整備しました。

---

## 作成したツール・ドキュメント

### 1. **JSONテンプレート** 📋
**ファイル**: `/home/user/stock_auto/data/macro_data_template.json`

**用途**: マクロ分析の全データを構造化されたJSON形式で保存するテンプレート

**内容**:
- 米国市場データ（NYダウ、S&P500、NASDAQ、Russell2000、SOX、VIX）
- 日本市場データ（日経平均、TOPIX、グロース250、売買代金、騰落銘柄数）
- 為替・コモディティ（USD/JPY、EUR/JPY、WTI、ゴールド、銅など）
- 金利・債券（米10年、日10年、スプレッド、逆イールド判定）
- 中央銀行政策（FRB、BOJ）
- インフレ指標（CPI、PCE、コア指標）
- 地政学リスク（イラン・中東、米中関係、ロシア・ウクライナ）
- 市場センチメント（VIX、Fear & Greed Index、投資家動向）
- テーマ別資金動向（AI・半導体、防衛、エネルギー、銀行、グロースなど）
- 総合判定（リスクオン/オフ、円安/円高、金利環境、セクター分化）

**利用方法**:
```bash
# テンプレートをコピーして、日付付きファイルを作成
cp data/macro_data_template.json reports/2026-06-24_macro_data.json

# テキストエディタまたはPythonで値を入力
vi reports/2026-06-24_macro_data.json

# JSON形式の検証
python3 -m json.tool reports/2026-06-24_macro_data.json
```

---

### 2. **データ収集ガイド** 📖
**ファイル**: `/home/user/stock_auto/docs/macro_data_collection_guide.md`

**用途**: マクロ分析に必要なデータの詳細な説明、取得方法、解釈方法をまとめたマニュアル

**セクション**:
1. **米国市場データ** - NYダウ、S&P500等の取得方法と解釈
2. **日本市場データ** - 日経平均、TOPIX、売買代金の詳細
3. **為替・コモディティ** - USD/JPY、原油、金、銅の説明と株式市場への波及メカニズム
4. **金利・債券** - 米国債・日本国債・逆イールド判定方法
5. **中央銀行・政策** - FRB・BOJのスタンス確認方法
6. **インフレ指標** - CPI、PCE、コアPCEの違いと重要性
7. **地政学・リスク要因** - 各リスク要因の株式市場への波及経路
8. **市場センチメント** - VIX、Fear & Greed Index の読み方
9. **テーマ別資金動向** - 各セクターの強弱判定基準
10. **総合判定基準** - マクロ環境の総合評価方法
11. **日次運用フロー** - 営業日終場後の実施手順
12. **自動化オプション** - 将来的なPython API取得例
13. **トラブルシューティング** - Q&A
14. **参考リンク集** - 信頼できるデータソースURL一覧

**利用方法**:
```bash
# ドキュメント確認
less docs/macro_data_collection_guide.md

# セクション別に必要な説明を参照
# 例）「金利・債券」セクションで逆イールド判定方法を確認
```

---

### 3. **手動収集チェックリスト** ✅
**ファイル**: `/home/user/stock_auto/scripts/fetch_macro_data_manual.md`

**用途**: ブラウザでWebサイトを訪問し、データを記録するための実務的なチェックリスト

**特徴**:
- 各データポイントの【記録欄】がプリント可能な形式
- URLが直接リンク（クリックで該当サイトへ移動可能）
- 確認項目ごとにチェックボックス付き
- 初心者向けの詳細な説明

**利用方法**:

#### 方法1: ブラウザで直接確認（推奨）
```
1. scripts/fetch_macro_data_manual.md をブラウザで開く
2. 各URLをクリックして該当サイトへアクセス
3. 【記録欄】に値を記入
4. 全データ入力後、JSONファイルに転記
```

#### 方法2: プリント→手書き
```bash
# Markdownをテキストファイルとして印刷
cat scripts/fetch_macro_data_manual.md > /tmp/macro_checklist.txt
# プリンタで印刷後、手書きで記入
# スキャンして再度入力（オプション）
```

#### 方法3: 別環境での自動取得
```bash
# 個人PC など制限のない環境で以下を実行
python3 -c "
import yfinance as yf
import json

# 米国市場データ取得
dow = yf.Ticker('^DJI').info
sp500 = yf.Ticker('^GSPC').info
nasdaq = yf.Ticker('^IXIC').info

# 結果をJSON形式で出力
print(json.dumps({
    'dow_jones': dow.get('currentPrice'),
    'sp500': sp500.get('currentPrice'),
    'nasdaq': nasdaq.get('currentPrice')
}, indent=2))
"
```

---

## 推奨される日次運用フロー

### 営業日15:00-17:00（日本時間）に以下を実施

#### STEP 1: データ収集（約30分）
```bash
# チェックリストを用意
cat scripts/fetch_macro_data_manual.md

# 各URLをブラウザで開いて、値を記録
# 記録順序：
# 1. 米国市場（NYダウ、S&P500等）
# 2. 日本市場（日経平均、TOPIX等）
# 3. 為替・コモディティ（USD/JPY、原油等）
# 4. 金利（米10Y、日10Y等）
# 5. 中央銀行・政策（FRB、BOJ）
# 6. インフレ・地政学・センチメント
```

#### STEP 2: データ入力（約15分）
```bash
# テンプレートをコピー
cp data/macro_data_template.json reports/2026-06-24_macro_data.json

# JSONエディタで値を入力
# テキストエディタ または VS Code で編集
vi reports/2026-06-24_macro_data.json

# または Python スクリプトで一括入力（自作スクリプト）
```

#### STEP 3: データ検証（約5分）
```bash
# JSON形式チェック
python3 -m json.tool reports/2026-06-24_macro_data.json > /dev/null

# ファイル確認
ls -lh reports/2026-06-24_macro_data.json
```

#### STEP 4: Git へのコミット
```bash
# ステージング
git add reports/2026-06-24_macro_data.json

# コミット
git commit -m "Add macro analysis data for 2026-06-24"

# プッシュ（必要に応じて）
git push origin main
```

**所要時間**: 約50分 / 営業日

---

## ファイル構成

```
/home/user/stock_auto/
├── data/
│   └── macro_data_template.json         ← マクロデータテンプレート（JSON）
├── docs/
│   └── macro_data_collection_guide.md   ← 詳細ガイド（Markdown）
├── scripts/
│   └── fetch_macro_data_manual.md       ← チェックリスト（Markdown）
├── reports/
│   ├── 2026-06-24_macro_data.json       ← 出力ファイル（営業日ごと）
│   ├── 2026-06-24_screening.md          ← スクリーニング結果
│   ├── 2026-06-24_evaluation.md         ← 評価結果
│   └── ...
├── CLAUDE.md                             ← プロジェクト指示
└── MACRO_DATA_SETUP.md                   ← このファイル
```

---

## トラブルシューティング

### Q1. JSONファイルが壊れた場合は？
```bash
# 形式を確認
python3 -m json.tool reports/2026-06-24_macro_data.json

# エラーが出た場合は、最後の「}」を確認
# または template.json から再スタート
```

### Q2. Yahoo Finance にアクセスできない場合は？
**A.** 以下の代替ソースを使用：
- Google Finance: https://www.google.com/finance
- MarketWatch: https://www.marketwatch.com
- 日本市場：日経平均公式 https://nikkei.com/markets/index/

### Q3. リアルタイムデータが必要な場合は？
**A.** 個人PC（制限なし環境）で以下を実行：
```bash
pip install yfinance
python3 fetch_macro_data_api.py  # 自作スクリプト
```

### Q4. データの信頼性を確認したい場合は？
**A.** 複数ソースで確認：
- 米国市場：Yahoo Finance ＋ CNBC
- 日本市場：日経Web ＋ 株式新聞
- 金利：Trading Economics ＋ 公開サイト

---

## 今後の拡張・自動化案

### フェーズ2: API連携（条件付き）
セキュリティポリシー許可後：
```bash
# yfinance で自動取得
python3 << 'EOF'
import yfinance as yf
import json
from datetime import datetime

data = {
    'date': datetime.now().strftime('%Y-%m-%d'),
    'dow_jones': yf.Ticker('^DJI').info.get('currentPrice'),
    'sp500': yf.Ticker('^GSPC').info.get('currentPrice'),
    # ... その他
}

with open(f'reports/{data["date"]}_macro_data.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
EOF
```

### フェーズ3: マクロ分析レポート自動生成
JSONデータを読み込んで、マクロレポート（.md）を自動生成

```python
# マクロレポート自動生成スクリプト（実装例）
def generate_macro_report(json_file):
    """JSONファイルからマクロレポートを生成"""
    with open(json_file) as f:
        data = json.load(f)
    
    report = f"""
# マクロ分析レポート：{data['date']}

## 米国市場
- NYダウ: {data['us_market']['dow_jones']['closing_value']}
...
"""
    return report
```

---

## 参考資料

### 推奨データソース（信頼性順）

**米国市場**:
1. Yahoo Finance (https://finance.yahoo.com)
2. CNBC Markets (https://www.cnbc.com/markets/)
3. Bloomberg (要サブスク)

**日本市場**:
1. 日本経済新聞 (https://nikkei.com/markets/)
2. 株式新聞 Web (https://www.kabusin.com)
3. 東証公式 (https://www.jpx.co.jp)

**グローバル指標**:
1. Trading Economics (https://tradingeconomics.com)
2. Federal Reserve (https://www.federalreserve.gov)
3. 日本銀行 (https://www.boj.or.jp)

---

## まとめ

### このセットアップで実現できること

✅ **ネットワーク制限下での効率的なマクロデータ収集**
- チェックリスト形式で漏れのない収集
- URLリンク付きで簡単アクセス

✅ **構造化されたデータの保存・管理**
- JSON形式で機械可読
- 過去のマクロデータとの比較可能

✅ **投資判断の透明化**
- 定量データの明確な記録
- マクロ環境の客観的評価

✅ **スクリーニング・評価との連携**
- マクロデータをベースに銘柄評価
- テンバガー候補の絞り込み

### 推奨される開始時期

- **即時開始**: 本セットアップで手動収集を開始
- **1-2週間後**: 運用フローを最適化
- **1か月後**: Python自動化スクリプトの検討

---

**セットアップ完了日**: 2026-06-25  
**次回データ収集予定日**: 2026-06-26（営業日）  
**更新予定**: 営業日ごと（日本時間15:00以降）

---

## ご質問・問題報告

以下のファイルを参照してください：

- **詳細マニュアル**: `docs/macro_data_collection_guide.md`
- **運用チェックリスト**: `scripts/fetch_macro_data_manual.md`
- **テンプレートファイル**: `data/macro_data_template.json`

何か不明な点があれば、上記ドキュメントのセクションを確認するか、スクリプト内のコメントを参照してください。
