from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from services.llm_prompt import build_qa_prompt
from services.llm import ask_llm
from services.diagram import generate_mermaid
from services.index import rebuild_index, search_text, setup_index
from services.storage import list_files, read_file, save_file
from services.summary import generate_summaries, SUMMARY_PREFIX, sanitize_filename

# 設定 - パスの定義 --- (*1)
BASE_DIR = Path(__file__).resolve().parent
TEXT_DIR = BASE_DIR / "text"        # テキストファイルの保存先
DATA_DIR = BASE_DIR / "data"        # ベクトル検索用データの保存先
STATIC_DIR = BASE_DIR / "static"    # フロントエンド用の静的ファイル配置先
for path in (TEXT_DIR, DATA_DIR):
    path.mkdir(exist_ok=True)

# Flaskアプリの初期化とベクトル検索のセットアップ --- (*2)
app = Flask(__name__, static_folder=str(STATIC_DIR))
setup_index(TEXT_DIR, DATA_DIR)

@app.route("/")
def index():
    """index.htmlを返す"""  # --- (*3)
    return send_from_directory(STATIC_DIR, "index.html")

@app.get("/api/files")
def api_files():
    """テキストファイルの一覧を返すAPI"""  # --- (*4)
    return jsonify({"files": list_files(TEXT_DIR)})

@app.get("/api/file/<path:file_name>")
def api_file(file_name: str):
    """指定されたテキストファイルの内容を返すAPI"""  # --- (*5)
    try:
        name, content = read_file(TEXT_DIR, file_name)
    except FileNotFoundError:  # ファイルが見つからない場合
        return jsonify({"error": "ファイルが見つかりません。"}), 404
    except ValueError as e:  # ファイル名などのエラーが発生した場合
        return jsonify({"error": str(e)}), 400
    return jsonify({"file": name, "content": content})

@app.post("/api/save")
def api_save():
    """テキストファイルの内容を保存するAPI"""  # --- (*6)
    data = request.get_json(silent=True) or {}
    try:
        file_name = save_file(  # ファイルの保存処理
            text_dir=TEXT_DIR,
            file_name=data.get("file_name", ""),
            old_file_name=data.get("old_file_name", ""),
            content=data.get("content", ""),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    # 保存後にベクトル検索のインデックスを再構築する（非同期で実行）
    rebuild_index()
    return jsonify({"ok": True, "file": file_name})

@app.post("/api/ask")
def api_ask():
    """質問と関連資料を基にLLMに回答を生成させるAPI"""  # --- (*7)
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "質問を入力してください。"}), 400
    try:
        # 質問に関連するテキストチャンクをベクトル検索で取得
        contexts = search_text(question, top_k=5)
        # 質問と関連資料をプロンプトにしてLLMに回答を生成させる
        prompt = build_qa_prompt(question, contexts)
        answer = ask_llm(prompt).strip()
        # 質問と回答のやり取りをファイルに出力
        qa_name = f"{SUMMARY_PREFIX}QA--{question}.md"
        qa_name = sanitize_filename(qa_name)
        (TEXT_DIR / qa_name).write_text(f"# 質問\n{question}\n\n# 回答\n{answer}\n", encoding="utf-8")
    except Exception as e:
        return jsonify({"error": f"質問に失敗しました: {e}"}), 500
    return jsonify({"answer": answer, "contexts": contexts})

@app.post("/api/summarize")
def api_summarize():
    """テキストを要約して返すAPI"""  # --- (*8)
    data = request.get_json(silent=True) or {}
    focus = data.get("focus", "").strip()
    try:
        result = generate_summaries(text_dir=TEXT_DIR, focus=focus)
    except Exception as e:
        return jsonify({"error": f"要約処理に失敗しました: {e}"}), 500
    return jsonify(result)

@app.post("/api/diagram")
def api_diagram():
    """図を生成して返すAPI"""  # --- (*9)
    data = request.get_json(silent=True) or {}
    focus = data.get("focus", "").strip()
    try:
        result = generate_mermaid(TEXT_DIR, DATA_DIR, focus)
    except Exception as e:
        return jsonify({"error": f"作図生成に失敗しました: {e}"}), 500
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8888, debug=True)
