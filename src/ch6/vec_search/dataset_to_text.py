"""JSONファイルをテキストに変換するプログラム"""
import json
from pathlib import Path
from typing import Any

def to_text(value: Any) -> str:
    """JSONの値をテキストに変換する"""  # --- (*1)
    if value is None:
        return ""
    if isinstance(value, str):
        # PDFからの変換などで無駄なスペースが多いのでスペースを除去
        value = value.replace("\u3000", " ")  # 全角スペースを半角に
        value = value.replace(" ", "")  # 無駄なスペースを除去
        return value.strip()
    if isinstance(value, (list, tuple)):
        parts = [to_text(v) for v in value]
        return to_text("\n".join(p for p in parts if p))
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)

def make_markdown(data: dict[str, Any], source_name: str) -> str:
    """JSONデータからMarkdownテキストを生成する"""  # --- (*2)
    case_number = to_text(data.get("case_number")) or "-"
    case_name = to_text(data.get("case_name")) or "-"
    gist = to_text(data.get("gist"))
    contents = to_text(data.get("contents")) or "(記載なし)"
    # テキストを整形してMarkdown形式にする --- (*3)
    lines = [f"# {case_number} {case_name}", ""]
    if gist:
        lines.extend(["## 要約", "", gist, ""])
    lines.extend(["## 内容", "", contents, "",
                f"元ファイル: {source_name}", ""])
    return "\n".join(lines)

def convert(src_dir: Path, out_dir: Path) -> tuple[int, int]:
    """JSONファイルをMarkdownファイルに変換する"""  # --- (*4)
    out_dir.mkdir(parents=True, exist_ok=True)
    converted = 0
    skipped = 0
    # JSONファイルを順番に処理する --- (*5)
    for json_path in sorted(src_dir.glob("*.json")):
        if json_path.name == "list.json":  # リストファイルは変換対象外
            continue
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            skipped += 1
            continue
        # JSONデータからMarkdownテキストを生成して保存する --- (*6)
        markdown = make_markdown(data, json_path.name)
        output_path = out_dir / f"{json_path.stem}.md"
        output_path.write_text(markdown, encoding="utf-8")
        converted += 1
    return converted, skipped

if __name__ == "__main__":  #--- (*7)
    source_dir = Path("data_set/precedent/2020")
    output_dir = Path("docs")
    if not source_dir.exists() or not source_dir.is_dir():
        raise SystemExit(f"source dir not found: {source_dir}")
    c, s = convert(source_dir, output_dir)
    print(f"converted: {c}, skipped: {s}, output: {output_dir}")
