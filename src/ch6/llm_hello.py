from litellm import completion

# 下記のAPIキーを環境変数に登録していること
# - OPENAI_API_KEY
# - GEMINI_API_KEY
# - ANTHROPIC_API_KEY

# 利用するモデルの一覧 --- (*1)
models = [
    "claude-3-haiku-20240307",  # Anthropicのモデル
    "gemini/gemini-3.1-flash-lite-preview",  # Googleのモデル
    "gpt-5-nano",  # OpenAIのモデル
]
# 質問する内容 --- (*2)
question = """
日本で最も高い山とその標高を`["名前",標高]`で答えてください。
説明は不要、JSONデータのみで答えて。
"""
# 各モデルに質問して、回答を表示する --- (*3)
for model in models:
    print(f"📍 {model}:")  # モデル名を表示
    res = completion(
        model=model,
        messages=[
            {"role": "user", "content": question}
        ]
    )
    answer = res.choices[0].message.content
    # 改行を削除して答えを表示
    print(f"  😀 答え: {answer.replace('\n', '')}\n")
    