#!/bin/bash
# run_daily.sh - デイリーリサーチをSTEPごとに分割実行（CCRリモート環境用）
# 使い方:
#   bash scripts/run_daily.sh                  # 本日日付・未完了のSTEPから自動開始
#   bash scripts/run_daily.sh 2026-04-24       # 日付指定

DATE=${1:-$(date +%Y-%m-%d)}
MAX_RETRY=3

# -------------------------------------------------------
# ユーティリティ
# -------------------------------------------------------

log_step()    { echo ""; echo "========================================"; echo " $1"; echo "========================================"; }
log_success() { echo "[OK] $1"; }
log_skip()    { echo "[スキップ] $1"; }
log_fail()    { echo "[失敗] $1"; }

step_done() {
    case $1 in
        1) [ -f "reports/${DATE}_macro.md" ] ;;
        2) [ -f "reports/${DATE}_screening.md" ] ;;
        3) [ -f "reports/${DATE}_evaluation.md" ] ;;
        4) ls reports/${DATE}_deepdive_*.md 2>/dev/null | grep -q . ;;
        5) [ -f "reports/${DATE}_article_macro.md" ] && [ -f "reports/${DATE}_article_screening.md" ] ;;
    esac
}

run_step() {
    local step=$1
    local prompt=$2

    for i in $(seq 1 $MAX_RETRY); do
        echo "  実行中 (試行 $i/$MAX_RETRY)..."
        claude -p "$prompt"
        if step_done $step; then
            return 0
        fi
        echo "  出力ファイルが見つかりません。リトライします..."
        sleep 5
    done
    return 1
}

git_push() {
    local step=$1
    echo "  git push 実行中 (STEP ${step})..."
    git add reports/ targets/
    if git diff --cached --quiet; then
        echo "  コミット対象なし。スキップ。"
        return 0
    fi
    git commit -m "Add daily research STEP${step}: ${DATE}"
    git push origin main && log_success "git push 完了 (STEP ${step})" || log_fail "git push 失敗 (STEP ${step})"
}

# -------------------------------------------------------
# STEP 0：前提チェック
# -------------------------------------------------------

log_step "デイリーリサーチ開始：$DATE"

WATCHLIST="targets/${DATE}_watchlist.csv"
if [ ! -f "$WATCHLIST" ]; then
    log_fail "$WATCHLIST が見つかりません。watchlistを作成してから再実行してください。"
    exit 1
fi
log_success "watchlist確認: $WATCHLIST"

# -------------------------------------------------------
# STEP 1：マクロ分析
# -------------------------------------------------------

log_step "STEP 1：マクロ分析"
if step_done 1; then
    log_skip "reports/${DATE}_macro.md は作成済み"
else
    run_step 1 "実行日: ${DATE}
STEP 1（マクロ分析）のみ実行してください。

.claude/skills/macro.md のスキル手順に従い、${DATE} のマクロ分析を実施してください。
結果を reports/${DATE}_macro.md に保存して終了してください。
他のSTEPは実行しないでください。" || { log_fail "STEP 1 失敗。処理を中断します。"; exit 1; }
    log_success "STEP 1 完了"
    git_push 1
fi

# -------------------------------------------------------
# STEP 2：スクリーニング
# -------------------------------------------------------

log_step "STEP 2：スクリーニング"
if step_done 2; then
    log_skip "reports/${DATE}_screening.md は作成済み"
else
    step_done 1 || { log_fail "reports/${DATE}_macro.md が存在しません。STEP 1から再実行してください。"; exit 1; }
    run_step 2 "実行日: ${DATE}
STEP 2（スクリーニング）のみ実行してください。

前提ファイル: reports/${DATE}_macro.md（作成済み）
対象watchlist: targets/${DATE}_watchlist.csv

.claude/skills/screening.md のスキル手順に従い、スクリーニングを実施してください。
結果を reports/${DATE}_screening.md に保存して終了してください。
他のSTEPは実行しないでください。" || { log_fail "STEP 2 失敗。処理を中断します。"; exit 1; }
    log_success "STEP 2 完了"
    git_push 2
fi

# -------------------------------------------------------
# STEP 3：銘柄評価
# -------------------------------------------------------

log_step "STEP 3：銘柄評価"
if step_done 3; then
    log_skip "reports/${DATE}_evaluation.md は作成済み"
else
    step_done 2 || { log_fail "reports/${DATE}_screening.md が存在しません。STEP 2から再実行してください。"; exit 1; }
    run_step 3 "実行日: ${DATE}
STEP 3（銘柄評価）のみ実行してください。

前提ファイル:
- reports/${DATE}_macro.md（作成済み）
- reports/${DATE}_screening.md（作成済み）

.claude/skills/evaluation.md のスキル手順に従い、スクリーニング選出銘柄を評価してください。
結果を reports/${DATE}_evaluation.md に保存して終了してください。
他のSTEPは実行しないでください。" || { log_fail "STEP 3 失敗。処理を中断します。"; exit 1; }
    log_success "STEP 3 完了"
    git_push 3
fi

# -------------------------------------------------------
# STEP 4：詳細調査
# -------------------------------------------------------

log_step "STEP 4：詳細調査（上位2銘柄）"
if step_done 4; then
    log_skip "deepdiveファイルは作成済み"
else
    step_done 3 || { log_fail "reports/${DATE}_evaluation.md が存在しません。STEP 3から再実行してください。"; exit 1; }
    run_step 4 "実行日: ${DATE}
STEP 4（詳細調査）のみ実行してください。

前提ファイル:
- reports/${DATE}_macro.md（作成済み）
- reports/${DATE}_screening.md（作成済み）
- reports/${DATE}_evaluation.md（作成済み）

.claude/skills/deep-dive.md のスキル手順に従い、evaluation.md の総合スコア上位2銘柄を詳細調査してください。
各銘柄の結果を reports/${DATE}_deepdive_XXXX.md（XXXXは銘柄コード）に保存して終了してください。
他のSTEPは実行しないでください。" || { log_fail "STEP 4 失敗。処理を中断します。"; exit 1; }
    log_success "STEP 4 完了"
    git_push 4
fi

# -------------------------------------------------------
# STEP 5：記事作成・note投稿
# -------------------------------------------------------

log_step "STEP 5：記事作成 & note下書き投稿"
if step_done 5; then
    log_skip "記事ファイルは作成済み"
else
    step_done 4 || { log_fail "deepdiveファイルが存在しません。STEP 4から再実行してください。"; exit 1; }
    run_step 5 "実行日: ${DATE}
STEP 5（記事作成・note投稿）のみ実行してください。

前提ファイル（すべて作成済み）:
- reports/${DATE}_macro.md
- reports/${DATE}_screening.md
- reports/${DATE}_evaluation.md
- reports/${DATE}_deepdive_*.md

.claude/skills/article.md のスキル手順に従い、2種類の記事を作成・保存してnoteに下書き投稿してください。
- reports/${DATE}_article_macro.md を作成 → note投稿
- reports/${DATE}_article_screening.md を作成 → note投稿
完了後に終了してください。他のSTEPは実行しないでください。" || { log_fail "STEP 5 失敗。記事ファイルの保存状況を確認してください。"; }
    log_success "STEP 5 完了"
    git_push 5
fi

# -------------------------------------------------------
# 完了サマリー
# -------------------------------------------------------

log_step "デイリーリサーチ完了：$DATE"
echo "生成ファイル:"
ls reports/${DATE}_*.md 2>/dev/null | while read f; do echo "  - $(basename "$f")"; done
