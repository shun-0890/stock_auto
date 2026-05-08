"""
note.com に記事を下書きとして投稿するスクリプト。

使い方:
    python scripts/post_to_note.py reports/YYYY-MM-DD_article_macro.md
    python scripts/post_to_note.py reports/YYYY-MM-DD_article_screening.md

環境変数（.env または環境変数で設定）:
    NOTE_EMAIL    : note.com のログインメールアドレス
    NOTE_PASSWORD : note.com のパスワード
    HTTPS_PROXY   : プロキシURL（任意）
"""

import sys
import os
import json
import requests
from urllib.parse import unquote
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

NOTE_API_BASE = "https://note.com/api"
SESSION_FILE = Path(__file__).parent / ".note_session.json"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Origin": "https://note.com",
    "Referer": "https://note.com/login",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "X-Requested-With": "XMLHttpRequest",
}


def _get_proxies() -> dict | None:
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    if proxy:
        return {"http": proxy, "https": proxy}
    return None


def login(email: str, password: str) -> dict:
    """note.com にログインしてセッション情報を返す。"""
    resp = requests.post(
        f"{NOTE_API_BASE}/v1/sessions/sign_in",
        json={
            "login": email,
            "password": password,
            "g_recaptcha_response": "",
            "redirect_path": "https://note.com/",
        },
        headers={**DEFAULT_HEADERS, "Content-Type": "application/json"},
        proxies=_get_proxies(),
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"ログイン失敗: {resp.status_code} {resp.text}")

    data = resp.json()
    cookies = dict(resp.cookies)
    return {"cookies": cookies, "user": data.get("data", {})}


def load_session() -> dict | None:
    if SESSION_FILE.exists():
        return json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    return None


def save_session(session: dict):
    SESSION_FILE.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")


def verify_session(session: dict) -> bool:
    resp = requests.get(
        f"{NOTE_API_BASE}/v2/me",
        cookies=session["cookies"],
        headers=DEFAULT_HEADERS,
        proxies=_get_proxies(),
        timeout=30,
    )
    return resp.status_code == 200


def get_session(email: str, password: str) -> dict:
    session = load_session()
    if session and verify_session(session):
        print("既存セッションを使用します")
        return session

    print("note.com にログイン中...")
    session = login(email, password)
    save_session(session)
    print("ログイン成功・セッションを保存しました")
    return session


def _xsrf_token(cookies: dict) -> str:
    """Cookie の XSRF-TOKEN を URL デコードして返す。"""
    return unquote(cookies.get("XSRF-TOKEN", ""))


def parse_article(file_path: Path) -> tuple[str, str]:
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title, body_start = "", 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            body_start = i + 1
            break
    if not title:
        title = file_path.stem
    body = "\n".join(lines[body_start:]).strip()
    return title, body


def create_draft(session: dict, title: str, body: str) -> dict:
    """note.com に下書きを作成する（2ステップ）。"""
    cookies = session["cookies"]
    xsrf = _xsrf_token(cookies)
    proxies = _get_proxies()
    headers_post = {
        **DEFAULT_HEADERS,
        "Content-Type": "application/json",
        "Referer": "https://editor.note.com/",
        "X-XSRF-TOKEN": xsrf,
    }

    # Step 1: ノートの骨組みを作成
    resp1 = requests.post(
        f"{NOTE_API_BASE}/v1/text_notes",
        json={"template_key": None},
        cookies=cookies,
        headers=headers_post,
        proxies=proxies,
        timeout=30,
    )
    if resp1.status_code not in (200, 201):
        raise RuntimeError(f"ノート作成失敗: {resp1.status_code} {resp1.text}")

    note_data = resp1.json().get("data", {})
    note_id = note_data.get("id")
    note_key = note_data.get("key", "")
    if not note_id:
        raise RuntimeError(f"note_id が取得できませんでした: {resp1.text}")

    # Step 2: 下書き保存
    resp2 = requests.post(
        f"{NOTE_API_BASE}/v1/text_notes/draft_save",
        params={"id": note_id, "is_temp_saved": "true"},
        json={
            "name": title,
            "body": body,
            "body_length": len(body),
            "index": False,
            "is_lead_form": False,
            "image_keys": [],
        },
        cookies=cookies,
        headers=headers_post,
        proxies=proxies,
        timeout=30,
    )
    if resp2.status_code not in (200, 201):
        raise RuntimeError(f"下書き保存失敗: {resp2.status_code} {resp2.text}")

    return {"key": note_key, "id": note_id}


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
        sys.exit(1)

    print(f"対象ファイル: {article_path}")
    title, body = parse_article(article_path)
    print(f"タイトル: {title}")
    print(f"本文文字数: {len(body)} 文字")

    session = get_session(email, password)
    result = create_draft(session, title, body)

    note_key = result.get("key", "")
    note_url = f"https://note.com/drafts/{note_key}" if note_key else "（URLの取得に失敗）"
    print(f"\n下書き作成完了！")
    print(f"URL: {note_url}")
    return note_url


if __name__ == "__main__":
    main()
