"""LLMプロンプトを生成する関数群"""

def build_qa_prompt(question: str, contexts: list[dict]) -> str:
    """関連資料付きの質問応答用プロンプトを生成する"""  # --- (*1)
    ctx_lines = []
    for i, item in enumerate(contexts, start=1):
        file_name = item.get("file", "unknown")
        text = item.get("text", "")
        ctx_lines.append(f"[資料{i}] {file_name}\n{text}")
    ctx_text = "\n\n".join(ctx_lines) if ctx_lines else "資料はありません。"
    return (
        "あなたはノートアプリのアシスタントです。"
        "以下の関連資料を根拠に、質問へ日本語で正確に回答してください。"
        "根拠が不足する場合は、その旨を明記してください。\n"
        "出力はMarkdown形式で出力してください。\n\n"
        f"### 関連資料:\n{ctx_text}\n\n"
        f"### 質問:\n{question}\n"
    )

def build_summary_prompt(file_name: str, content: str, focus="") -> str:
    """単一ファイル要約用プロンプトを生成する"""  # --- (*2)
    focus_line = f"要約の観点: {focus}\n" if focus else ""
    return (
        "あなたはノートアプリのアシスタントです。\n"
        "次の文書を日本語で要約してください。\n"
        "重要な論点を抜き出して、最大5点ほどの箇条書きで出力してください。\n"
        "出力はMarkdown形式で出力してください。\n\n"
        f"{focus_line}"
        f"文書名: {file_name}\n\n"
        "入力文章:\n"
        f"{content}"
    )

def build_global_summary_prompt(summaries: str, focus="") -> str:
    """複数要約を統合する全体要約用プロンプトを生成する"""  # --- (*3)
    focus_line = f"要約の観点: {focus}\n" if focus else ""
    return (
        "あなたはノートアプリのアシスタントです。"
        "複数文書の要約を統合し、全体像が分かる日本語要約を作成してください。"
        "重複を整理して全体の流れと主要論点が分かるように約2000文字でまとめてください。"
        "箇条書きは最小限にしてください。\n\n"
        f"{focus_line}\n"
        f"{summaries}"
    )

def build_diagram_prompt(summary_text: str, focus="") -> tuple[str, str]:
    """Mermaid図を作るための作図用プロンプトを生成する"""  # --- (*4)
    # Mermaidのひな形
    mermaid_template = """
        graph LR
            A("主題")
            A --> B1["枝1"]
            A --> B2["枝2"]
            A --> B3["枝3"]
            B1 --> C1_1["枝1-1"]
            B1 --> C1_2["枝1-2"]
            B2 --> C2_1["枝2-1"]
            B2 --> C2_2["枝2-2"]
    """
    # システムプロンプトを用意
    sys_prompt = (
        "資料を基にして、Mermaid図を出力してください。\n"
        "次のひな形に、主題と枝1,枝2,枝3にキーワードを差し込んでください。\n"
        f"```mermaid\n{mermaid_template}\n```\n"
        "なお、Mermaidのコード以外は出力しないでください。"
    )
    # ユーザープロンプトを用意
    focus_line = f"作図の観点: {focus}\n" if focus else ""
    user_prompt = (
        "指示: 以下の資料に基づいてMermaidを完成させてください。\n"
        f"{focus_line}資料:\n{summary_text}"
    )
    return sys_prompt, user_prompt
