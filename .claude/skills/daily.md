# デイリー自動実行

毎日のリサーチフローをワンコマンドで一気通貫に実行します。
途中でユーザーへの確認は不要です。各ステップを順番に完遂してください。

## 実行順序

以下の4ステップを **必ず順番に** 実行する。前のステップが完了してから次へ進む。

---

### STEP 1：マクロ分析
`macro.md` スキルの手順に従い、詳細マクロ分析を実施する。
→ `reports/YYYY-MM-DD_macro.md` を生成して保存する。

---

### STEP 2：スクリーニング
`screening.md` スキルの手順に従い、STEP 1のマクロ分析結果を踏まえてスクリーニングを実施する。
→ `reports/YYYY-MM-DD_screening.md` を生成して保存する。

---

### STEP 3：銘柄評価
`evaluation.md` スキルの手順に従い、STEP 2で選出された銘柄を評価する。
→ `reports/YYYY-MM-DD_evaluation.md` を生成して保存する。

---

### STEP 4：詳細調査（上位2銘柄）
`deep-dive.md` スキルの手順に従い、STEP 3の評価で総合スコアが上位2銘柄を対象に詳細調査を実施する。
上位2銘柄の選定基準：★合計スコアが高い順。同点の場合は独自技術（軸1）のスコアが高い方を優先。
→ `reports/YYYY-MM-DD_deepdive_XXXX.md` を銘柄ごとに生成して保存する（2ファイル）。

---

## 完了時の出力

全ステップ完了後、以下のサマリーを出力する：

```
# デイリーリサーチ完了：YYYY-MM-DD

## 生成ファイル
- reports/YYYY-MM-DD_macro.md
- reports/YYYY-MM-DD_screening.md
- reports/YYYY-MM-DD_evaluation.md
- reports/YYYY-MM-DD_deepdive_XXXX.md
- reports/YYYY-MM-DD_deepdive_YYYY.md

## 本日の投資環境
（マクロ総合判断を1〜2行で）

## スクリーニング選出：X銘柄

## 評価上位2銘柄
| 銘柄 | スコア | 判定 | 買い推奨 |
|------|--------|------|---------|
| XXXX 〇〇〇〇 | XX/20 | S/A | Yes/No |
| YYYY 〇〇〇〇 | XX/20 | S/A | Yes/No |

## 次のアクション
（詳細調査結果を踏まえた具体的な投資行動の示唆）
```
