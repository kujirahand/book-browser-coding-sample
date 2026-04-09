"""docs配下テキストを読んでFAISSインデックスを作成"""
import json
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# インデックス作成の設定 --- (*1)
ROOT_DIR = Path(__file__).parent
DOCS_DIR = Path(ROOT_DIR, "docs")
DATA_DIR = Path(ROOT_DIR, "data")
INDEX_PATH = Path(DATA_DIR, "docs.faiss")
META_PATH = Path(DATA_DIR, "docs_meta.json")
# 使用するSentenceTransformerモデル
MODEL_NAME = "intfloat/multilingual-e5-small"
E5_PASSAGE_PREFIX = "passage: "

def split_text(text: str, size = 800, overlap = 200) -> list[str]:
    """文字数ベースで重なり付きチャンクに分割する。""" # --- (*2)
    text = text.strip()
    if not text:
        return []
    # チャンクのリストを作成
    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = end - overlap
    return chunks

def collect_chunks(docs_dir: Path) -> list[dict]:
    """docs内のMarkdownを読み込み、チャンクとメタ情報を集める""" # --- (*3)
    records: list[dict] = []
    for path in sorted(docs_dir.glob("*.md")):
        # テキストを読み込む --- (*4)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        # テキストをチャンクに分割してrecordsに追加 --- (*5)
        chunks = split_text(text)
        for i, chunk in enumerate(chunks):
            records.append({
                    "source": path.name,
                    "chunk_id": i,
                    "text": chunk,
            })
    return records

def build_index(records: list[dict], model_name: str) -> faiss.Index:
    """FAISSインデックスを構築する""" # --- (*6)
    model = SentenceTransformer(model_name)
    # テキストをベクトル化 --- (*7)
    # E5系モデル推奨の接頭辞を文書側に付ける
    texts = [f"{E5_PASSAGE_PREFIX}{r['text']}" for r in records]
    emb = model.encode(  # テキストをベクトル化
        texts,
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    # ベクトルをfloat32に変換してL2正規化
    emb = np.asarray(emb, dtype="float32")
    faiss.normalize_L2(emb)
    # インデックスを作成してベクトルを追加
    dim = emb.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(emb)
    return index

def main() -> None:
    """docs配下テキストを読んでFAISSインデックスを作成して保存する""" # --- (*8)
    if not DOCS_DIR.exists():
        raise SystemExit(f"フォルダがありません: {DOCS_DIR}")
    DATA_DIR.mkdir(parents=True, exist_ok=True)  # データフォルダを作成
    # docs内のMarkdownを読み込み、チャンクとメタ情報を集める --- (*9)
    records = collect_chunks(DOCS_DIR)
    index = build_index(records, model_name=MODEL_NAME)
    # インデックスとメタ情報を保存 --- (*10)
    faiss.write_index(index, str(INDEX_PATH))
    META_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"インデックスを作成しました。{len(records)}チャンクを保存")

if __name__ == "__main__":
    main()
