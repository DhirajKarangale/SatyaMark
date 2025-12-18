import json
import re
from typing import Dict, Any

from connect import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


llm = get_llm("deepseek_r1")


PROMPT_TEMPLATE = """
You are a factual verification assistant.

You do NOT have access to the internet, news, or private data.
Use ONLY your internal general knowledge.

Task:
Classify the statement as:
- Correct
- Incorrect
- Insufficient

Rules:
- Do NOT guess.
- If unsure, choose Insufficient.
- Insufficient is valid.

Return a JSON object with:
mark, confidence (0-100), and a VERY DETAILED reason.

Statement:
{text}
"""


prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
parser = StrOutputParser()


def _invoke(text: str) -> str:
    try:
        out = (prompt | llm | parser).invoke({"text": text})

        if hasattr(out, "content"):
            return out.content
        if isinstance(out, dict) and "text" in out:
            return out["text"]
        return str(out)

    except Exception:
        return ""

def _parse(raw: str) -> Dict[str, Any]:
    # 1. Remove DeepSeek reasoning
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    # 2. Remove markdown code fences
    raw = re.sub(r"```(?:json)?", "", raw, flags=re.IGNORECASE).strip()

    # DEBUG (keep while testing)
    # print("CLEANED OUTPUT:\n", raw)

    # 3. Extract JSON object
    match = re.search(r"\{[\s\S]*?\}", raw)
    if not match:
        raise ValueError("No JSON found")

    data = json.loads(match.group(0))

    mark = data.get("mark", "").strip()
    confidence = int(data.get("confidence", 0))
    reason = data.get("reason", "").strip()

    if mark not in {"Correct", "Incorrect", "Insufficient"}:
        raise ValueError("Invalid mark")

    confidence = max(0, min(confidence, 100))

    if not reason:
        raise ValueError("Empty reason")

    return {
        "mark": mark,
        "confidence": confidence,
        "reason": reason,
    }

def fact_check(text: str) -> dict:
    if not text or not text.strip():
        return {
            "mark": "Insufficient",
            "confidence": 0,
            "reason": "No valid statement was provided for fact checking.",
        }

    try:
        raw = _invoke(text)
        # return raw
        return _parse(raw)

    except Exception:
        return {
            "mark": "Insufficient",
            "confidence": 0,
            "reason": (
                "The language model did not return a reliably structured factual "
                "analysis. To avoid guessing or hallucinating, the claim is marked "
                "as Insufficient."
            ),
        }
