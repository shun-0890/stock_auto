"""
note.com に記事を下書きとして投稿するスクリプト。

使い方:
    python scripts/post_to_note.py reports/YYYY-MM-DD_article_macro.md
    python scripts/post_to_note.py reports/YYYY-MM-DD_article_screening.md

環境変数（.env または環境変数で設定）:
    NOTE_EMAIL    : note.com のログインメールアドレス
    NOTE_PASSWORD : note.com のパスワード
"""

import sys
import os
import re
import json
import requests
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

NOTE_API_BASE = "https://note.com/api"
SESSION_FILE = Path(__file__).parent / ".note_session.json"


def login(email: str, password: str) -> dict:
    """note.com にログインしてセッション情報を返す。"""
    resp = requests.post(
        f"{NOTE_API_BASE}/v2/sessions",
        json={"login": email, "password": password},
        headers={"Content-Type": "application/json"},
    )
    if resp.status_code != 200:
        raise RuntimeError(f"ログイン失敗: {resp.status_code} {resp.text}")

    data = resp.json()
    cookies = dict(resp.cookies)
    return {"cookies": cookies, "user": data.get("data", {})}


def load_session() -> dict | None:
    """保存済みセッションを読み込む。"""
    if SESSION_FILE.exists():
        return json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    return None


def save_session(session: dict):
    SESSION_FILE.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")


def verify_session(session: dict) -> bool:
    """セッションが有効かどうか確認する。"""
    resp = requests.get(
        f"{NOTE_API_BASE}/v2/me",
        cookies=session["cookies"],
    )
    return resp.status_code == 200


def get_session(email: str, password: str) -> dict:
    """有効なセッションを取得する（キャッシュ優先）。"""
    session = load_session()
    if session and verify_session(session):
        print("既存セッションを使用します")
        return session

    print("note.com にログイン中...")
    session = login(email, password)
    save_session(session)
    print("ログイン成功・セッションを保存しました")
    return session


def parse_article(file_path: Path) -> tuple[str, str]:
    """Markdownファイルからタイトルと本文を抽出する。"""
    text = file_path.read_text(encoding="utf-8")

    # 1行目の `# タイトル` をタイトルとして使用
    lines = text.splitlines()
    title = ""
    body_start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            # 【YYYY/MM/DD】などのプレフィックスをそのまま使う
            body_start = i + 1
            break

    if not title:
        title = file_path.stem  # ファイル名をフォールバック

    body = "\n".join(lines[body_start:]).strip()
    return title, body


def create_draft(session: dict, title: str, body: str) -> dict:
    """note.com に下書きを作成する。"""
    resp = requests.post(
        f"{NOTE_API_BASE}/v1/text_notes",
        json={
            "name": title,
            "body": body,
            "status": "draft",
            "price": 0,
        },
        cookies=session["cookies"],
        headers={"Content-Type": "application/json"},
    )
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"下書き作成失敗: {resp.status_code} {resp.text}")
    return resp.json()


def main():
    if len(sys.argv) < 2:
        print("使い方: python scripts/post_to_note.py <記事ファイルパス>")
        sys.exit(1)

    article_path = Path(sys.argv[1])
    if not article_path.exists():
        print(f"ファイルが見つかりません: {article_path}")
        sys.exit(1)

    email = os.environ.get("NOTE_EMAIL")
    password = os.environ.get("NOTE_PASSWORD")
    if not email or not password:
        print("環境変数 NOTE_EMAIL / NOTE_PASSWORD が設定されていません。")
        print(".env ファイルに記載するか、環境変数に設定してください。")
        sys.exit(1)

    print(f"対象ファイル: {article_path}")
    title, body = parse_article(article_path)
    print(f"タイトル: {title}")
    print(f"本文文字数: {len(body)} 文字")

    session = get_session(email, password)
    result = create_draft(session, title, body)

    note_data = result.get("data", {})
    note_key = note_data.get("key", "")
    note_url = f"https://note.com/drafts/{note_key}" if note_key else "（URLの取得に失敗）"

    print(f"\n下書き作成完了！")
    print(f"URL: {note_url}")
    return note_url


if __name__ == "__main__":
    main()
