"""LLMを使ったファクトチェック処理をまとめたモジュール"""
import asyncio
import json
import re
from collections import Counter
from litellm import acompletion
from llm_prompt import MODELS, SYSTEM_PROMPT, VERDICT_LABELS

async def ask_llm(claim: str, model: str) -> dict:
    """モデルに問い合わせて、判定結果を辞書で返す"""  # --- (*1)
    user_prompt = f"次の主張を判定してください:\n\n{claim}"
    # LiteLLMのacompletion関数を呼び出す
    resp = await acompletion(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    # 返ってきた応答からJSONを抽出して辞書に変換する --- (*2)
    content = resp.choices[0].message.content
    data = extract_json(content)
    return {
        "model": model,
        "verdict": normalize_verdict(data.get("verdict")),
        "confidence": max(0.0, min(1.0, float(data.get("confidence", 0.0)))),
        "summary": str(data.get("summary", "")),
        "content": str(data.get("content", "")),
    }

def aggregate_results(claim: str, results: list[dict]) -> dict:
    """複数のモデルの結果を集約して、最終的な判定と要約を作成する"""  # --- (*3)
    # 各モデルの判定を集計して最も多いものを最終判定とする
    verdicts = [str(r.get("verdict", "根拠不足")) for r in results]
    counts = Counter(verdicts)
    final_verdict = counts.most_common(1)[0][0] if counts else "根拠不足"
    top_count = counts[final_verdict]
    # モデル間の一致度に応じた要約を作成
    if top_count == len(results) and len(results) > 0:
        agreement_score = 1.0
        summary = "満場一致で判定しました。"
    elif top_count >= 2:
        agreement_score = 2 / 3
        summary = "二者が一致しましたが異論があります。"
    else:
        agreement_score = 1 / 3
        summary = "モデル間で見解が割れています。追加の証拠確認が必要です。"
    return {
        "claim": claim,
        "final_verdict": final_verdict,
        "agreement_score": agreement_score,
        "summary": summary,
        "results": results,
    }

async def run_fact_check(claim: str) -> dict:
    """複数モデルでファクトチェックを実行して集約結果を返す"""  # --- (*4)
    tasks = [ask_llm(claim, model) for model in MODELS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # 結果をまとめる
    ok_results: list[dict] = []
    for i, result in enumerate(results):
        model = MODELS[i]
        if isinstance(result, dict):  # 正しく処理できた場合
            result["model"] = model
            ok_results.append(result)
            continue
        ok_results.append({  # エラーが発生している場合
                "model": model,
                "verdict": "根拠不足",
                "confidence": 0.0,
                "summary": "モデル呼び出し失敗",
                "content": str(result),
        })
    return aggregate_results(claim, ok_results)

def extract_json(text: str) -> dict:
    """モデルの応答からJSON部分を抽出して辞書に変換する""" # --- (*5)
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)  # 不要なコードブロックを削除
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    # 最初の { から最後の } を抽出
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        raise ValueError("JSONが見つかりません")
    return json.loads(m.group(0))

def normalize_verdict(value: object) -> str:
    """モデルの応答からverdictを正規化する"""  # --- (*6)
    if not isinstance(value, str):
        return "根拠不足"
    for label in VERDICT_LABELS:
        if label in value:
            return label
    return "根拠不足"
