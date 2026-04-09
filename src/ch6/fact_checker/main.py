"""ファクトチェックするためのFastAPIアプリ"""
import json
import uvicorn

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from llm_factchecker import run_fact_check

# FastAPIアプリの定義 --- (*1)
app = FastAPI(title="ファクトチェック")
# 静的ファイルを提供するためのルートを追加 --- (*2)
app.mount("/static", StaticFiles(directory="static"), name="static")

# APIエンドポイントの定義 --- (*3)
@app.get("/")
def index():
    """static/index.htmlにリダイレクト"""  # --- (*4)
    return RedirectResponse(url="/static/index.html", status_code=307)

@app.post("/api/fact-check")
async def fact_check(req: Request):
    """APIでファクトチェックを実行するエンドポイント"""  #-- (*5)
    try:
        # JSON形式のリクエストボディを読み取る --- (*6)
        payload = await req.json()
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="JSON形式が不正です") from exc
    # 送られてきた主張を取得 --- (*7)
    claim = payload.get("claim", "").strip()
    if claim == "":
        raise HTTPException(status_code=422, detail="主張が空です。")
    return await run_fact_check(claim)

if __name__ == "__main__":
    # 開発用サーバーを起動 --- (*8)
    uvicorn.run(app, host="127.0.0.1", port=8000)
