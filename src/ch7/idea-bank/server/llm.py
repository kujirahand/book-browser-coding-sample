"""LLM関連の処理をまとめるモジュール"""
import json
import os
import re
from typing import Any
from litellm import completion
from llm_prompt import LLM_SYSTEM_PROMPT, build_analysis_prompt

def ask_llm(sys_prompt: str, user_prompt: str) -> dict[str, Any]:
    """LLMへ問い合わせてJSON応答を辞書で返す""" # --- (*1)
    print("LLMへ送信:\n", sys_prompt, "\n", user_prompt)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        response = completion(
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        print("LLMの応答:\n",content)
        return parse_json_from_text(content)
    except Exception:
        return {}

def build_idea_analysis(text: str) -> dict[str, Any]:
    """本文からタイトル要約タグ発展案を組み立てる""" # --- (*2)
    llm_data = ask_llm(LLM_SYSTEM_PROMPT, build_analysis_prompt(text))
    return {
        "title": _normalize_space(llm_data.get("title", "")),
        "summary": _normalize_space(llm_data.get("summary", "")),
        "tags": unique_list(llm_data.get("tags")),
        "ideas": unique_list(llm_data.get("ideas")),
    }

def parse_json_from_text(text: str) -> dict[str, Any]:
    """テキストからJSONオブジェクトを抽出して返す""" # --- (*3)
    content = (text or "").strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    try:
        parsed = json.loads(content)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}

def _normalize_space(text: str) -> str:
    """連続する空白を単一スペースに正規化する"""
    return re.sub(r"\s+", " ", str(text)).strip()

def unique_list(raw: Any) -> list[str]:
    """値を重複なしの文字列リストへ整形する"""
    if not isinstance(raw, list):
        return []
    return list(dict.fromkeys(v for v in (item for item in raw) if v))
