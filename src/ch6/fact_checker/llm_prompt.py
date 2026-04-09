"""利用するモデルやプロンプトをまとめたもの"""
# 使いたいモデルの一覧 --- (*1)
MODELS = [
    "claude-haiku-4-5",  # Anthropicのモデル
    "gemini/gemini-3.1-flash-lite-preview",  # Googleのモデル
    "gpt-5-nano",  # OpenAIのモデル
]

# 判定の種類を表す型とラベル --- (*2)
VERDICT_LABELS = ["正しい", "間違い", "不明", "根拠不足"]

# システムプロンプトの指定 --- (*3)
SYSTEM_PROMPT = f"""
あなたは厳格なファクトチェック支援AIです。
与えられた主張について、断定しすぎず、曖昧さを明示してください。

### 出力形式:
必ず次の形式のJSONのみを返してください。説明文やコードブロックは禁止です。
```json
{{
    "verdict": "{'|'.join(VERDICT_LABELS)}",
    "confidence": 0.0,
    "summary": "100文字以内の短い要約",
    "content": "1000文字以内で理由を説明",
}}
```
- confidence は 0.0-1.0 の範囲で指定してください。
- verdict は {','.join(VERDICT_LABELS)} のいずれかで指定してください。
"""
