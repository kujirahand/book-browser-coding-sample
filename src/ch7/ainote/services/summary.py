from pathlib import Path
from services.llm_prompt import build_summary_prompt, build_global_summary_prompt
from services.llm import ask_llm

# 要約ファイルのプレフィクスと全体要約ファイル名の定義 --- (*1)
SUMMARY_PREFIX = "(要約)"
SUMMARY_ALL_FILE = f"{SUMMARY_PREFIX}全体--.md"

def list_source_files(text_dir: Path) -> list[Path]:
    """要約ファイルを除いた要約対象ファイル一覧を返す"""  # --- (*2)
    files = [p for p in text_dir.glob("*.md")
             if not p.name.startswith(SUMMARY_PREFIX)]
    return sorted(files, key=lambda x: x.name.lower())

def generate_summaries(text_dir: Path, focus: str = "") -> dict:
    """各ファイル要約と全体要約を生成"""  # --- (*3)
    # 要約対象のファイル一覧を取得
    files = list_source_files(text_dir)
    # 各ファイルを順番に要約 --- (*4)
    summaries = []
    for path in files:
        # 要約の保存ファイル名を決定して正規化 --- (*5)
        summary_name = f"{SUMMARY_PREFIX}{path.stem}--{focus}.md"
        summary_name = sanitize_filename(summary_name)
        summary_path = text_dir / summary_name
        # 対象テキストファイル内容を読み込む --- (*6)
        try:
            content = path.read_text(encoding="utf-8").strip()
        except Exception as e:
            print(f"[ERROR] ファイル {path.name} の読み込みに失敗: {e}")
            continue
        if not content:
            continue
        # ファイルごとの要約プロンプトを作成して要約を生成 --- (*7)
        prompt = build_summary_prompt(path.name, content, focus)
        summary = ask_llm(prompt).strip()
        # 要約を保存する
        summary_path.write_text(summary + "\n", encoding="utf-8")
        summaries.append({
            "source_file": path.name,
            "summary_file": summary_name,
            "summary": summary
        })
    if not summaries:
        return {"summaries": [], "overall_summary": "",
                "display_text": "要約元がありません。"}
    # 全体の要約を生成して保存する --- (*8)
    merged = "\n\n--------------\n\n".join(
        [f"## {item['source_file']}\n{item['summary']}" for item in summaries]
    )
    overall_name = f"{SUMMARY_PREFIX}全体--{focus}.md"
    overall_name = sanitize_filename(overall_name)  # ファイル名を安全に正規化
    overall_path = text_dir / overall_name
    # 全体要約プロンプトを作成して要約を生成 --- (*9)
    overall_prompt = build_global_summary_prompt(merged, focus)
    overall_summary = ask_llm(overall_prompt).strip()
    overall_path.write_text(overall_summary + "\n", encoding="utf-8")
    # 表示用のテキストを作成して返す
    sections = [
        f"# {item['summary_file']}\n{item['summary']}"
        for item in summaries
    ]
    sections.append(f"# {overall_name}\n{overall_summary}")
    return {
        "summaries": summaries,
        "overall_summary": overall_summary,
        "display_text": "\n\n".join(sections),
    }

def sanitize_filename(name: str) -> str:
    """要約ファイル名を安全なMarkdownファイル名に正規化"""  # --- (*10)
    safe = Path(name.strip()).name
    safe = safe[:-3] if safe.endswith(".md") else safe
    if not safe:
        raise ValueError("要約ファイル名が空です。")
    if safe in {".", ".."}:
        raise ValueError("不正な要約ファイル名です。")
    return f"{safe}.md"
