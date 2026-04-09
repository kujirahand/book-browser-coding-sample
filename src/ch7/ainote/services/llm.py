from litellm import completion, embedding

# 利用するモデルを指定 --- (*1)
AI_MODEL = "ollama/gemma3n:e4b"  # あるいは、"ollama/qwen3.5:4b"
API_BASE = "http://localhost:11434"  # OllamaのAPIエンドポイント
EXTRA = {"think": False} # Thinkモードをオフにして高速に応答を得る
# Embedding用のモデルを指定
EMBEDDING_MODEL = "ollama/qwen3-embedding:4b"

# (参考) クラウドモデルを指定する場合 --- (*2)
# AI_MODEL = "gpt-5-mini"
# API_BASE = None
# EXTRA = None

def ask_llm(question: str, sys_prompt="") -> str:
    """LLMに質問を投げて回答を得る"""  # -- (*3)
    print("[DEBUG] LLMに与えるプロンプト:\n" + question)
    msg = [{"role": "user", "content": question}]
    if sys_prompt:
        msg.insert(0, {"role": "system", "content": sys_prompt})
    response = completion(
        model=AI_MODEL,
        messages=msg,
        api_base=API_BASE,
        extra_body=EXTRA,
    )
    result = response.choices[0].message.content
    print("[DEBUG] LLMからの回答:\n" + result)
    return result


def get_embedding(text_list: list[str]) -> list[list[float]]:
    """文字列リストをEmbeddingに変換"""  # --- (*4)
    response = embedding(
        model=EMBEDDING_MODEL,
        input=text_list,
        api_base=API_BASE,
    )
    # Embeddingだけを抽出して出力
    result = []
    for d in response.data:
        result.append(d["embedding"])
    return result
