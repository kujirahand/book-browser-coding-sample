from flask import Flask, jsonify, request, abort
from storage import create_idea, get_idea, list_idea_items, normalize_space

# アイデアバンクの管理画面とAPIを提供するFlaskアプリ --- (*1)
app = Flask(__name__)

# ルーティングとAPIエンドポイントの定義 --- (*2)
@app.route("/")
def index():
    """管理画面のトップページを返す"""
    return app.send_static_file("index.html")

@app.route("/api/ideas", methods=["GET"])
def list_ideas():
    """保存済みアイデア一覧を返す""" # -- (*3)
    return jsonify(list_idea_items())

@app.route("/api/ideas", methods=["POST"])
def save_idea():
    """受け取った本文を解析してアイデアとして保存""" # --- (*4)
    payload = request.get_json(silent=True) or {}
    text = normalize_space(payload.get("text", ""))
    if not text:
        return jsonify({"error": "text is required"}), 400
    # アイデアを保存する
    saved = create_idea(
        text,
        str(payload.get("url", "")),
        str(payload.get("page_title", "")))
    return jsonify(saved), 201

@app.route("/api/ideas/<path:idea_id>", methods=["GET"])
def get_idea_by_id(idea_id: str):
    """指定したアイデアの詳細を返す""" # --- (*5)
    try:
        return jsonify(get_idea(idea_id))
    except FileNotFoundError:
        abort(404, description="idea not found")

if __name__ == "__main__": # --- (*6)
    app.run(port=8000, debug=True)
