# デイリー自動実行

毎日のリサーチフローをワンコマンドで一気通貫に実行します。
途中でユーザーへの確認は不要です。各ステップを順番に完遂してください。

## 実行順序

以下のステップを **必ず順番に** 実行する。前のステップが完了してから次へ進む。

## 注意事項

- タイムアウト等が発生して作業が中断してしまった場合はリトライをする。3度リトライしても同じエラーで作業が先に勧められなかった場合は自動実行を終了すること。

---

### STEP 0：watchlistの存在確認

`targets/YYYY-MM-DD_watchlist.csv`（YYYY-MM-DDは実行日の日付）が存在するか確認する。

- **ファイルが存在しない場合：** 以降のステップを実行せず、以下のメッセージを出力して終了する。
  ```
  [自動実行スキップ] targets/YYYY-MM-DD_watchlist.csv が見つかりません。
  watchlistを作成してから再実行してください。
  ```
- **ファイルが存在する場合：** STEP 1へ進む。

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

### STEP 5：記事作成 & note下書き投稿

`article.md` スキルの手順に従い、2種類の記事を作成してnoteに下書き投稿する。

**5-1. マクロ分析記事の作成**
- STEP 1の結果をもとに `article.md` の「記事①：マクロ分析記事」の構成で執筆する
- `reports/YYYY-MM-DD_article_macro.md` に保存する
- 以下のコマンドでnoteに下書き投稿する：
  ```
  python scripts/post_to_note.py reports/YYYY-MM-DD_article_macro.md
  ```

**5-2. 銘柄スクリーニング記事の作成**
- STEP 2〜4の結果をもとに `article.md` の「記事②：銘柄スクリーニング記事」の構成で執筆する
- `reports/YYYY-MM-DD_article_screening.md` に保存する
- 以下のコマンドでnoteに下書き投稿する：
  ```
  python scripts/post_to_note.py reports/YYYY-MM-DD_article_screening.md
  ```

投稿に失敗した場合は3回リトライする。3回とも失敗した場合は記事ファイルの保存までを完了とし、投稿失敗をサマリーに記録して次のステップへ進む。

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
- reports/YYYY-MM-DD_article_macro.md
- reports/YYYY-MM-DD_article_screening.md

## note下書き投稿
- マクロ記事：（投稿URL または 失敗理由）
- スクリーニング記事：（投稿URL または 失敗理由）

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
