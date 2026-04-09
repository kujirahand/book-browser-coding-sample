"""最小構成の判例検索サーバー"""
import json
from pathlib import Path
from typing import Any, cast
import faiss
import numpy as np
from flask import Flask, jsonify, request, redirect
from sentence_transformers import SentenceTransformer

# 検索サーバーの設定情報 --- (*1)
ROOT_DIR = Path(__file__).parent
DATA_DIR = Path(ROOT_DIR, "data")
INDEX_PATH = Path(DATA_DIR, "docs.faiss")
META_PATH = Path(DATA_DIR, "docs_meta.json")
MODEL_NAME = "intfloat/multilingual-e5-small"
E5_QUERY_PREFIX = "query: "
HOST = "127.0.0.1"
PORT = 8000
STATE: dict[str, object] = {  # サーバーの状態を保存
    "index": None,
    "meta": [],
    "model": None,
}

# Flaskサーバーのオブジェクトを生成 --- (*2)
app = Flask(__name__, static_folder="static")

def main() -> None:
    """インデックスなどを読み込んでサーバーを開始する"""  # --- (*3)
    if not (INDEX_PATH.exists() and META_PATH.exists()):
        raise SystemExit(f"インデックスが見当たりません: {INDEX_PATH}")
    load_assets(INDEX_PATH, META_PATH, MODEL_NAME)
    app.run(host=HOST, port=PORT, debug=True)

def load_assets(index_path: Path, meta_path: Path, model_name: str) -> None:
    """インデックスとメタデータ、モデルを読み込んでSTATEに保存"""  # --- (*4)
    STATE["index"] = faiss.read_index(str(index_path))
    STATE["meta"] = json.loads(meta_path.read_text(encoding="utf-8"))
    STATE["model"] = SentenceTransformer(model_name)


def search_records(query: str, top_k: int = 5) -> list[dict]:
    """STATE上のモデルとインデックスで類似検索を実行する。"""  # --- (*5)
    top_k = max(1, min(top_k, 50))
    model = cast(SentenceTransformer, STATE["model"])
    index = cast(faiss.Index, STATE["index"])
    meta = cast(list[dict], STATE["meta"])

    # クエリーをベクトルデータにエンコード --- (*6)
    q_vec = model.encode([f"{E5_QUERY_PREFIX}{query}"],
        convert_to_numpy=True, normalize_embeddings=True)
    q_vec = np.asarray(q_vec, dtype="float32")
    faiss.normalize_L2(q_vec)
    # 類似度の高い上位K件を取得 --- (*7)
    index_any = cast(Any, index)
    scores, ids = index_any.search(q_vec, top_k)
    results: list[dict] = []
    for score, idx in zip(scores[0], ids[0]):
        if idx < 0 or idx >= len(meta):
            continue
        rec = meta[idx]
        results.append({
            "score": float(score),
            "source": rec.get("source", ""),
            "chunk_id": rec.get("chunk_id", -1),
            "text": rec.get("text", ""),
        })
    return results

@app.get("/")
def root():
    """static/index.htmlにリダイレクト"""  # --- (*8)
    return redirect("/static/index.html")

@app.get("/search")
def search():
    """クエリーを受け取って検索結果を返す"""  # --- (*9)
    # 検索クエリーを取得
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "q is required"}), 400
    try:
        top_k = int(request.args.get("top_k", 5))
    except ValueError:
        top_k = 5
    # 検索を実行してJSONで結果を返す
    results = search_records(q, top_k=top_k)
    return jsonify({"query": q, "top_k": top_k, "results": results})

if __name__ == "__main__":
    main()
