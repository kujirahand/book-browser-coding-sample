"""広告ブロッカーのルール管理サーバー"""
import json
from pathlib import Path
from typing import Any
import uvicorn
from fastapi import FastAPI, Form

# ルールを保存するファイルのパス --- (*1)
DATA_FILE = Path(__file__).with_name("rules.json")
# デフォルトのドメインリスト
DEFAULT_DOMAINS = [
    "doubleclick.net",
    "googlesyndication.com",
    "ads.yahoo.co.jp",
]
# ブラウザのWebRequest APIで使用されるリソースタイプ
RESOURCE_TYPES = [
    "main_frame",
    "sub_frame",
    "script",
    "xmlhttprequest",
    "image",
    "font",
    "media",
]
# FastAPIアプリケーションのインスタンスを作成 --- (*2)
app = FastAPI(title="Dynamic Rule API")

@app.get("/")
def index() -> str:
    """サーバ−にアクセスしたとき"""  # --- (*3)
    return "APIは稼働しています"

@app.get("/domains")
def get_domains() -> dict[str, list[str]]:
    """保存されたドメインリストを出力する"""  # --- (*4)
    return {"domains": _load_domains()}

@app.get("/rules")
def get_rules() -> dict[str, Any]:
    """保存されたドメインリストをDNRルールの形式で出力する"""
    domains = _load_domains()
    return {"rules": [_to_dnr_rule(i + 1, domain) for i, domain in enumerate(domains)]}

@app.post("/edit")
def edit_rules(domains: str = Form(default="")) -> dict[str, Any]:
    """ドメインリストを編集して保存"""  # --- (*5)
    lines = domains.splitlines()
    _save_domains(lines)
    saved = _load_domains()
    return {"ok": True, "count": len(saved)}

def _normalize_domains(domains: list[str]) -> list[str]:
    """ドメインリストを正規化して重複を削除する"""  # --- (*6)
    cleaned = [d.strip() for d in domains if d.strip()]
    return list(dict.fromkeys(cleaned))

def _load_domains() -> list[str]:
    """保存されたドメインリストを読み込む"""  # --- (*7)
    if not DATA_FILE.exists():
        return DEFAULT_DOMAINS.copy()
    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    if isinstance(raw, list) and all(isinstance(item, str) for item in raw):
        return _normalize_domains(raw)
    return DEFAULT_DOMAINS.copy()

def _save_domains(domains: list[str]) -> None:
    """ドメインリストを保存する"""  # --- (*8)
    DATA_FILE.write_text(
        json.dumps(_normalize_domains(domains), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def _to_dnr_rule(rule_id: int, domain: str) -> dict[str, Any]:
    """ドメインをDNRルールの形式に変換する"""  # --- (*9)
    return {
        "id": rule_id,
        "priority": 1,
        "action": {"type": "block"},
        "condition": {
            "urlFilter": f"||{domain}^",
            "resourceTypes": RESOURCE_TYPES,
        },
    }

if __name__ == "__main__":  # サーバーを起動 --- (*10)
    uvicorn.run("server.main:app", host="127.0.0.1", port=8000, reload=True)
