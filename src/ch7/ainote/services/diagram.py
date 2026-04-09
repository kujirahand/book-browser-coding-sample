import re
from pathlib import Path
from services.llm_prompt import build_diagram_prompt
from services.llm import ask_llm
from services.index import search_text
from services.summary import SUMMARY_ALL_FILE, generate_summaries

def extract_mermaid(text: str) -> str:
    """LLM出力からMermaidコードを抽出する"""
    match = re.search(
        r"```mermaid\s*(.*?)```", text,
        flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    pos = text.lower().find("mindmap")
    return text[pos:].strip() if pos >= 0 else text.strip()

def format_context_chunks(contexts: list[dict]) -> str:
    """検索で得た関連チャンクを作図入力向けテキストに整形する"""
    lines: list[str] = []
    for i, item in enumerate(contexts, start=1):
        file_name = item.get("file", "unknown")
        text = item.get("text", "")
        lines.append(f"[資料{i}] {file_name}\n{text}")
    return "\n\n----------------\n\n".join(lines).strip()


def resolve_draw_source(text_dir: Path, focus: str) -> str:
    """作図ソースを決定"""
    # 検索語句を元に作図ソースを検索
    if focus:
        print("[DEBUG] 作図のための関連資料を検索しています...")
        contexts = search_text(focus, top_k=8)
        if not contexts:
            raise ValueError("focusに関連する資料が見つかりませんでした。")
        return format_context_chunks(contexts)
    # テキストの要約を作図ソースにする
    summary_path = text_dir / SUMMARY_ALL_FILE
    if not summary_path.exists():  # 既に要約があればそれを使う
        generate_summaries(text_dir=text_dir, focus="")
    return summary_path.read_text(encoding="utf-8").strip()


def generate_mermaid(text_dir: Path, data_dir: Path, focus: str) -> dict:
    """作図ソースからMermaidコードを生成して保存し結果を返す"""
    source_text = resolve_draw_source(text_dir, focus)
    sys_prompt, user_prompt = build_diagram_prompt(source_text, focus)
    llm_output = ask_llm(user_prompt, sys_prompt=sys_prompt)
    mermaid_code = extract_mermaid(llm_output)
    (data_dir / "mindmap.mmd").write_text(mermaid_code + "\n", encoding="utf-8")
    return {"mermaid": mermaid_code, "raw": llm_output}
