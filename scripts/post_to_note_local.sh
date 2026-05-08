#!/bin/bash
# ローカルマシンから note.com に下書き投稿するスクリプト
# 使い方:
#   bash scripts/post_to_note_local.sh YYYY-MM-DD
#
# 事前準備:
#   pip install requests python-dotenv
#   .env に NOTE_EMAIL / NOTE_PASSWORD を設定しておく

DATE=${1:-$(date +%Y-%m-%d)}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$REPO_ROOT" || exit 1

MACRO_FILE="reports/${DATE}_article_macro.md"
SCREENING_FILE="reports/${DATE}_article_screening.md"

echo "============================="
echo " note.com 下書き投稿（ローカル実行）"
echo " 対象日付: ${DATE}"
echo "============================="

if [ ! -f "$MACRO_FILE" ] && [ ! -f "$SCREENING_FILE" ]; then
    echo "[エラー] 記事ファイルが見つかりません: ${DATE}"
    exit 1
fi

if [ -f "$MACRO_FILE" ]; then
    echo ""
    echo ">>> マクロ記事を投稿中..."
    python scripts/post_to_note.py "$MACRO_FILE" && echo "[成功]" || echo "[失敗]"
fi

if [ -f "$SCREENING_FILE" ]; then
    echo ""
    echo ">>> スクリーニング記事を投稿中..."
    python scripts/post_to_note.py "$SCREENING_FILE" && echo "[成功]" || echo "[失敗]"
fi

echo ""
echo "============================="
echo " 完了"
echo "============================="
