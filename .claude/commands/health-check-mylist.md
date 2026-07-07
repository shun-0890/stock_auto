`.claude/skills/portfolio-review/SKILL.md` のスキル手順に従い、保有銘柄の最新ヘルスチェックを実施してください。

## 実行手順

1. `mylist/holdings.csv` を読み込む。ファイルが存在しない場合はユーザーに保有銘柄を確認する。
2. 本日日付（$DATE または今日の日付）を基準に、各銘柄の最新情報を収集・分析する。
3. スキル手順の判定基準に従い、各銘柄の推奨アクション（損切 / 利益確定 / 押し目買い / ホールド継続）を決定する。
4. 結果を `reports/YYYY-MM-DD_portfolio_review.md` に保存する。
