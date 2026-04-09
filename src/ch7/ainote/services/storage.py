from pathlib import Path

from services.summary import SUMMARY_PREFIX

def normalize_file_name(name: str) -> str:
    """入力値を安全なMarkdownファイル名に正規化する"""
    safe = Path(name.strip()).name
    safe = safe[:-3] if safe.endswith(".md") else safe
    if not safe:
        raise ValueError("ファイル名を入力してください。")
    if safe in {".", ".."}:
        raise ValueError("不正なファイル名です。")
    return f"{safe}.md"

def get_text_path(text_dir: Path, file_name: str) -> Path:
    """textディレクトリ内の安全なファイルパスを返す"""
    safe_name = Path(file_name).name
    path = (text_dir / safe_name).resolve()
    if path.parent != text_dir.resolve():
        raise ValueError("不正なパスです。")
    return path

def list_files(text_dir: Path) -> list[str]:
    """要約ファイルを除いたファイル名一覧を返す"""
    files = list(text_dir.glob("*.md"))
    return sorted([f.name for f in files], key=str.lower)

def list_source_files(text_dir: Path) -> list[Path]:
    """要約ファイルを除いたPath一覧を返す"""
    files = [p for p in text_dir.glob("*.md") if not p.name.startswith(SUMMARY_PREFIX)]
    return sorted(files, key=lambda x: x.name.lower())


def read_file(text_dir: Path, file_name: str) -> tuple[str, str]:
    """指定ファイルを読み込みファイル名と本文を返す"""
    path = get_text_path(text_dir, file_name)
    if not path.exists():
        raise FileNotFoundError("ファイルが見つかりません。")
    return path.name, path.read_text(encoding="utf-8")


def save_file(
    text_dir: Path,
    file_name: str,
    old_file_name: str,
    content: str,
) -> str:
    """ファイルを保存し必要に応じて旧ファイル名を削除する"""
    new_name = normalize_file_name(file_name)
    new_path = get_text_path(text_dir, new_name)
    new_path.write_text(content, encoding="utf-8")

    if old_file_name:
        old_safe = normalize_file_name(old_file_name)
        if old_safe != new_name:
            old_path = get_text_path(text_dir, old_safe)
            if old_path.exists():
                old_path.unlink()
    return new_name
