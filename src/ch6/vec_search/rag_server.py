"""RAGで回答を返すFlaskサーバー"""
import os
from typing import Any, cast
from flask import Flask, jsonify, request, redirect
from litellm import completion
import search_server
# RAGサーバーの設定 --- (*1)
MODEL_NAME = "gpt-5-mini"
TOP_K = 10
HOST = "127.0.0.1"
PORT = 8010
# Flaskサーバーのオブジェクトを生成 --- (*2)
app = Flask(__name__, static_folder="static")

def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """ベクトル検索を行ってチャンクの一覧を得る"""  # --- (*3)
    if search_server.STATE["model"] is None:
        search_server.load_assets(  # アセットをロード
            search_server.INDEX_PATH,
            search_server.META_PATH,
            search_server.MODEL_NAME,
        )
    return search_server.search_records(query, top_k=top_k)

def build_context(results: list[dict]) -> str:
    """検索結果をプロンプト用の文脈文字列に整形"""  # --- (*4)
    lines: list[str] = []
    for i, item in enumerate(results, start=1):
        source = item.get("source", "")
        score = item.get("score", 0.0)
        text = item.get("text", "")
        lines.append(f"[資料{i}] source={source} score={score:.4f}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines).strip()

def answer_question(question: str) -> tuple[str, list[dict]]:
    """検索結果を根拠にLLMで回答を生成する"""  # --- (*5)
    results = retrieve(question, top_k=TOP_K)
    context = build_context(results)
    # プロンプトを指定 --- (*6)
    system_prompt = (
        "あなたは判例検索のアシスタントです。"
        "与えられた資料だけを根拠に日本語で簡潔に回答してください。"
        "資料に十分な根拠がない場合は、その旨を明示してください。"
        "分かりやすい言葉で親切に答えてください。"
        "Markdownで出力してください。"
    )
    user_prompt = (
        f"質問:\n{question}\n\n"
        f"検索資料:\n{context}\n\n"
        "回答形式:\n"
        "# (タイトル)\n"
        "## 回答\n(ここにMakdown形式で回答)\n\n"
        "### 根拠(使った資料番号とsource)"
    )
    # LLMに回答を生成させる --- (*7)
    response = completion(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    response_any = cast(Any, response)
    answer = response_any.choices[0].message.content or ""
    return answer, results

@app.get("/")
def root():
    """static/llm.htmlにリダイレクト"""  # --- (*8)
    return redirect("/static/llm.html")

@app.get("/ask")
def ask():
    """クエリを受け取りRAG回答を返す"""  # --- (*9)
    if not os.environ.get("OPENAI_API_KEY"):
        return jsonify({"error": "OPENAI_API_KEYが未設定です。"}), 500
    # クエリーqを取得
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "q is required"}), 400
    try:
        # RAGで質問に回答
        answer, results = answer_question(q)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    # 実行結果をJSONで返す
    return jsonify(
        {
            "question": q,
            "answer": answer,
            "contexts": [
                {
                    "source": r.get("source", ""),
                    "score": r.get("score", 0.0),
                    "chunk_id": r.get("chunk_id", -1),
                }
                for r in results
            ],
        }
    )

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True) # --- (*10)
