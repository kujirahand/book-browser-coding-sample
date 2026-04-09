"""LLMに与えるプロンプトを定義したモジュール"""
# 作図のためのプロンプト --- (*1)
GENERATE_PROMPT = (
    "あなたはMermaid図を生成するアシスタントです。"
    "Mermaidコードのみを出力してください。"
    "説明文、Markdown記法、コードフェンスは出力しないでください。"
)
# 壊れたMermaidコードを修正するプロンプト --- (*2)
FIX_PROMPT = (
    "あなたはMermaid構文エラーを修正するアシスタントです。"
    "修正後のMermaidコードのみを出力してください。"
    "説明文、Markdown記法、コードフェンスは出力しないでください。"
    "記号があるとエラーになるので[\"A + B\"]のようにダブルクオートで囲んでください。"
)

def build_generate_user_prompt(user_input: str) -> str:
    """図生成用のユーザープロンプトを組み立てる。""" # --- (*3)
    return (
        "次の内容を表すシンプルで読みやすいMermaid図を作成してください。\n"
        f"内容:\n{user_input}"
    )

def build_fix_user_prompt(code: str, error: str) -> str:
    """エラー修正用のユーザープロンプトを組み立てる。""" # --- (*4)
    return (
        "次のMermaidコードを、エラー内容に基づいて修正してください。\n"
        f"エラー: {error}\n"
        f"コード:\n{code}"
    )
