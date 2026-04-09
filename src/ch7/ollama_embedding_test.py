from litellm import embedding

# Embedding用のモデルを指定 --- (*1)
EMBEDDING_MODEL = "ollama/qwen3-embedding:4b"
API_BASE = "http://localhost:11434"  # OllamaのAPIエンドポイント

def get_embedding(text_list: list[str]) -> list[list[float]]:
    """文字列リストをEmbeddingに変換"""  # --- (*2)
    response = embedding(
        model=EMBEDDING_MODEL,
        input=text_list,
        api_base=API_BASE,
    )
    # Embeddingだけを抽出して出力 --- (*3)
    result = []
    for d in response.data:
        result.append(d["embedding"])
    return result

if __name__ == "__main__":
    # Embeddingのテスト --- (*4)
    print(get_embedding(["これはテストです。"]))
