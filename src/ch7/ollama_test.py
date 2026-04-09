from litellm import completion

# Ollamaでダウンロードしたモデルを指定 --- (*1)
MODEL = "ollama/qwen3.5:4b"
THINK_MODE = False  # Trueにすると長考してから回答する
# 質問を指定 --- (*2)
QUESTION = "世界的に有名な仕事に役立つ格言を一つ教えて。"
# APIを呼び出して回答を得る --- (*3)
response = completion(
    model=MODEL,
    messages=[
        {"role": "user", "content": QUESTION}
    ],
    api_base="http://localhost:11434",
    extra_body={"think": THINK_MODE, "max_tokens": 1000},
)
print(response.choices[0].message.content)
