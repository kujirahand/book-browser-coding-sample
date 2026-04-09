import os
from flask import Flask, jsonify, request
import webview
from litellm import completion
from llm_prompt import (
    FIX_PROMPT,
    GENERATE_PROMPT,
    build_fix_user_prompt,
    build_generate_user_prompt,
)

# バックエンドのサーバーFlaskを準備 --- (*1)
server = Flask(__name__, static_folder="static")

def ask_llm(system_prompt: str, user_prompt: str) -> str:
    """LLMに問い合わせ、Mermaidコードを返す""" # --- (*2)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    print("=== LLMに送るプロンプト ===\n", messages)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    resp = completion(
        model=model,
        messages=messages,
        temperature=0.1,
    )
    text = resp.choices[0].message.content.strip()
    print("=== LLMの応答 ===\n", text)
    return text.replace("```mermaid", "").replace("```", "").strip()

@server.get("/")
def index():
    """アプリのトップページを返す""" #--- (*3)
    return server.send_static_file("index.html")

@server.post("/api/generate")
def generate():
    """入力テキストからMermaid図を生成して返すAPI""" # --- (*4)
    prompt = request.json.get("prompt", "").strip()
    if not prompt:
        return jsonify({"code": "graph LR\nA[プロンプトが空です]"})
    code = ask_llm(GENERATE_PROMPT, build_generate_user_prompt(prompt))
    return jsonify({"code": code})


@server.post("/api/fix")
def fix():
    """Mermaidコードとエラー内容を受け取り、修正版コードを返すAPI""" # --- (*5)
    code = request.json.get("code", "")
    error = request.json.get("error", "")
    prompt = build_fix_user_prompt(code, error)
    return jsonify({"code": ask_llm(FIX_PROMPT, prompt)})

if __name__ == "__main__":
    # ウィンドウを表示する --- (*6)
    webview.create_window("Diagram", server, width=1200, height=800)
    webview.start()
