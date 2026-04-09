import json
import threading
from pathlib import Path
import numpy as np
import faiss
from services.llm import get_embedding
from services.summary import SUMMARY_PREFIX

def is_summary_markdown(file_name: str) -> bool:
    """要約ファイル名かどうかを判定"""
    return file_name.startswith(SUMMARY_PREFIX)

_lock = threading.Lock()
_state = {
    "text_dir": None,
    "data_dir": None,
    "chunk_size": 500,
    "overlap": 80,
    "index": None,
    "vectors": None,
    "meta": [],
    "bootstrap_attempted": False,
    "index_path": None,
    "meta_path": None,
    "vectors_path": None,
}


def setup_index(text_dir, data_dir) -> None:
    """ベクトル検索の設定とインデックス読み込みを行う"""
    t_dir = Path(text_dir)
    d_dir = Path(data_dir)
    d_dir.mkdir(exist_ok=True)
    with _lock:
        _state["chunk_size"] = 500
        _state["overlap"] = 80
        _state["text_dir"] = t_dir
        _state["data_dir"] = d_dir
        _state["index_path"] = d_dir / "faiss.index"
        _state["meta_path"] = d_dir / "faiss_meta.json"
        _state["vectors_path"] = d_dir / "vectors.npy"
        _state["bootstrap_attempted"] = False
    _load_index()


def _rebuild_index_sync() -> None:
    """テキストを再分割して埋め込みを作りインデックスを再構築"""
    _require_setup()
    with _lock:
        _state["bootstrap_attempted"] = True
    chunks = _collect_chunks()
    if not chunks:
        with _lock:
            _state["index"] = None
            _state["vectors"] = None
            _state["meta"] = []
        _persist_index(None, None, [])
        return
    vectors = np.array(get_embedding([chunk["text"] for chunk in chunks]), dtype="float32")
    index = None
    if faiss is not None:
        index = faiss.IndexFlatL2(vectors.shape[1])
        index.add(vectors)
    with _lock:
        _state["index"] = index
        _state["vectors"] = vectors
        _state["meta"] = chunks
    _persist_index(index, vectors, chunks)


def rebuild_index() -> None:
    """インデックス再構築をバックグラウンド実行"""

    def _safe_rebuild() -> None:
        """再構築処理を安全に実行する"""
        try:
            _rebuild_index_sync()
        except Exception:
            pass

    threading.Thread(target=_safe_rebuild, daemon=True).start()


def search_text(query: str, top_k: int = 5) -> list[dict]:
    """質問文に近いテキストチャンクを上位件数だけ返す"""
    _require_setup()
    _ensure_index()
    with _lock:
        index = _state["index"]
        vectors = _state["vectors"]
        meta = list(_state["meta"])
    if not meta:
        return []

    q_vec = np.array(get_embedding([query]), dtype="float32")
    k = min(top_k, len(meta))
    if index is not None:
        distances, ids = index.search(q_vec, k)
    else:
        if vectors is None:
            return []
        diff = vectors - q_vec[0]
        all_dist = np.sum(diff * diff, axis=1)
        sorted_ids = np.argsort(all_dist)[:k]
        ids = np.array([sorted_ids], dtype=np.int64)
        distances = np.array([all_dist[sorted_ids]], dtype=np.float32)

    results = []
    for idx, dist in zip(ids[0], distances[0]):
        if idx < 0 or idx >= len(meta):
            continue
        item = dict(meta[idx])
        item["distance"] = float(dist)
        results.append(item)
    return results


def _require_setup() -> None:
    """インデックス設定済みか確認し未設定なら例外を送出する"""
    if _state["text_dir"] is None or _state["data_dir"] is None:
        raise RuntimeError("index_service is not initialized. call setup_vec_search() first.")


def _ensure_index() -> None:
    """未構築時に初回インデックス構築を試行する"""
    with _lock:
        has_data = bool(_state["meta"])
        attempted = bool(_state["bootstrap_attempted"])
    if has_data or attempted:
        return
    try:
        _rebuild_index_sync()
    except Exception:
        with _lock:
            _state["bootstrap_attempted"] = True


def _load_index() -> bool:
    """保存済みインデックスとメタ情報を読み込み成功可否を返す"""
    meta_path: Path | None = _state["meta_path"]
    index_path: Path | None = _state["index_path"]
    vectors_path: Path | None = _state["vectors_path"]
    if meta_path is None or index_path is None or vectors_path is None or not meta_path.exists():
        return False
    try:
        meta_raw = json.loads(meta_path.read_text(encoding="utf-8"))
        if not isinstance(meta_raw, list) or not meta_raw:
            return False
        meta = [dict(item) for item in meta_raw]
    except Exception:
        return False

    index = None
    vectors = None
    if faiss is not None and index_path.exists():
        try:
            index = faiss.read_index(str(index_path))
        except Exception:
            index = None
    if index is None and vectors_path.exists():
        try:
            vectors = np.load(vectors_path).astype("float32")
        except Exception:
            vectors = None
    if index is None and vectors is None:
        return False
    if vectors is not None and len(meta) != len(vectors):
        return False
    if index is not None and index.ntotal != len(meta):
        return False

    with _lock:
        _state["index"] = index
        _state["vectors"] = vectors
        _state["meta"] = meta
    return True


def _persist_index(index, vectors: np.ndarray | None, chunks: list[dict[str, str]]) -> None:
    """インデックスとメタ情報をファイルへ保存する"""
    index_path: Path | None = _state["index_path"]
    meta_path: Path | None = _state["meta_path"]
    vectors_path: Path | None = _state["vectors_path"]
    if index_path is None or meta_path is None or vectors_path is None:
        return
    if not chunks or vectors is None:
        for path in [index_path, meta_path, vectors_path]:
            if path.exists():
                path.unlink()
        return

    meta_path.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    np.save(vectors_path, vectors)
    if index is not None and faiss is not None:
        faiss.write_index(index, str(index_path))
    elif index_path.exists():
        index_path.unlink()


def _collect_chunks() -> list[dict[str, str]]:
    """要約以外のテキストから検索用チャンクを収集する"""
    text_dir: Path | None = _state["text_dir"]
    if text_dir is None:
        return []

    chunks: list[dict[str, str]] = []
    for path in sorted(text_dir.glob("*.md")):
        if is_summary_markdown(path.name):
            continue
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        for chunk in _split_text(content):
            chunks.append({"file": path.name, "text": chunk})
    return chunks


def _split_text(text: str) -> list[str]:
    """段落を維持しながら指定サイズで分割する"""
    chunk_size = int(_state["chunk_size"])
    normalized = text.replace("\r\n", "\n")
    paragraphs = [p.strip() for p in normalized.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_split_long_text(paragraph))
            continue
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = paragraph
    if current:
        chunks.append(current)
    return chunks


def _split_long_text(text: str) -> list[str]:
    """長文をオーバーラップ付きで分割する"""
    chunk_size = int(_state["chunk_size"])
    overlap = int(_state["overlap"])
    if len(text) <= chunk_size:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks
