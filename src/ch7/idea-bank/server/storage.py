from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any
from llm import build_idea_analysis, unique_list

# アイデアの保存と読み込みを担当するモジュール --- (*1)
BASE_DIR = Path(__file__).resolve().parent
IDEAS_DIR = BASE_DIR / "ideas"
IDEAS_DIR.mkdir(parents=True, exist_ok=True)

def create_idea(text: str, url: str, src_title: str) -> dict[str, Any]:
    """本文とソース情報から新しいアイデアを保存して返す""" # --- (*2)
    # LLMを用いて本文を解析
    clean_text = normalize_space(text)
    now = datetime.now()
    analysis = build_idea_analysis(clean_text)
    title = analysis.get("title") or "untitled"
    # 本文をファイルに保存
    text_path = get_save_filename(title, now)  # ファイル名を決定
    text_path.write_text(clean_text + "\n", encoding="utf-8")
    # メタデータを保存
    meta_data = {
        "title": normalize_space(title),
        "summary": normalize_space(analysis.get("summary", "")),
        "tags": unique_list(analysis.get("tags")),
        "ideas": unique_list(analysis.get("ideas")),
        "source_url": url,
        "source_title": src_title,
    }
    json_str = json.dumps(meta_data, ensure_ascii=False, indent=2)
    json_path = text_path.with_suffix(".json")
    json_path.write_text(json_str, encoding="utf-8")
    return parse_idea_file(text_path)

def load_idea_metadata(path: Path) -> dict[str, Any]:
    """メタデータJSONを読み込み整形して返す""" # --- (*3)
    json_path = path.with_suffix(".json")
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data

def get_save_filename(title: str, now: datetime) -> Path:
    """重複しない保存パスを作成する""" # --- (*4)
    fname = sanitize_filename(title[:20])
    stem = f"{now.year}{now.month:02d}{now.day:02d}-{fname}"
    candidate = IDEAS_DIR / f"{stem}.md"
    # ファイル名が被るとき連番を振って重複しないファイル名を見つける
    serial = 2
    while candidate.exists():
        candidate = IDEAS_DIR / f"{stem}-{serial}.md"
        serial += 1
    return candidate

def parse_idea_file(path: Path) -> dict[str, Any]:
    """本文とメタデータを統合したアイデア辞書を返す""" # --- (*5)
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    meta = load_idea_metadata(path) or {}
    rel = path.relative_to(IDEAS_DIR).as_posix()
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return {
        "id": rel,
        "title": meta.get("title") or path.stem,
        "summary": meta.get("summary") or "",
        "tags": meta.get("tags") or [],
        "ideas": meta.get("ideas") or [],
        "source_url": meta.get("source_url") or "",
        "source_title": meta.get("source_title") or "",
        "text": text,
        "created_at": mtime.strftime("%Y/%m/%d %H:%M:%S"),
    }

def list_idea_paths() -> list[Path]:
    """保存済みMarkdownのパス一覧を新しい順で返す""" # --- (*6)
    files = IDEAS_DIR.rglob("*.md")
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)

def list_idea_items(index=0, n=50) -> list[dict[str, Any]]:
    """アイデア一覧を本文付きで返す""" # --- (*7)
    paths = list_idea_paths()[index:n]  # indexからn件だけ得る
    return [parse_idea_file(path) for path in paths]

def resolve_idea_path(idea_id: str) -> Path:
    """IDからMarkdownのファイルパスに変換""" # --- (*8)
    path = (IDEAS_DIR / idea_id).resolve()
    # ディレクトリトラバーサル対策
    if IDEAS_DIR.resolve() not in path.parents:
        raise FileNotFoundError("idea not found")
    # ファイルが存在しないときもエラー
    if not path.exists() or not path.is_file():
        raise FileNotFoundError("idea not found")
    return path

def get_idea(idea_id: str) -> dict[str, Any]:
    """指定IDのアイデア詳細を返す""" # --- (*9)
    return parse_idea_file(resolve_idea_path(idea_id))

def normalize_space(text: str) -> str:
    """連続する空白を単一スペースに正規化する"""
    return re.sub(r"\s+", " ", str(text)).strip()

def sanitize_filename(title: str) -> str:
    """タイトルを安全なファイル名へ変換する"""
    safe = re.sub(r"[\\/:*?\"<>|\s]+", "-", title).strip("-")[:40]
    return safe or "untitled"
