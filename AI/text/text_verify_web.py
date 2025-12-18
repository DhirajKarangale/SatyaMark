import json
from typing import Any, Dict, List
from connect import get_llm


FORBIDDEN_PHRASES = (
    "provided web evidence",
    "provided web information",
    "given data",
    "given evidence",
    "provided data",
    "provided information",
)


# -----------------------------
# Utilities
# -----------------------------

def _strip_noise(text: str) -> str:
    if not isinstance(text, str):
        return ""
    while "<think>" in text and "</think>" in text:
        s = text.find("<think>")
        e = text.find("</think>") + len("</think>")
        text = text[:s] + text[e:]
    return text.replace("```json", "").replace("```", "").strip()


def _safe_parse_json(raw: Any) -> Dict[str, Any]:
    try:
        if hasattr(raw, "content"):
            raw_text = raw.content
        elif isinstance(raw, dict):
            raw_text = raw.get("content", "")
        elif isinstance(raw, str):
            raw_text = raw
        else:
            return {}

        raw_text = _strip_noise(raw_text)
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return {}
        return json.loads(raw_text[start : end + 1])
    except Exception:
        return {}


def _clean_web_data(web_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    cleaned = []
    for entry in web_data or []:
        try:
            url = str(entry.get("url", "")).strip()
            data = str(entry.get("data", "")).strip()
            if not url or not data:
                continue
            if len(data) < 50:
                continue
            lowered = data.lower()
            if lowered in ("n/a", "not found", "error", "undefined"):
                continue
            cleaned.append({"url": url, "data": data})
        except Exception:
            continue
    return cleaned


def _sanitize_reason(reason: str) -> str:
    r = reason
    for phrase in FORBIDDEN_PHRASES:
        r = r.replace(phrase, "publicly reported information")
    return r.strip()


def _confidence_for_insufficient(num_sources: int) -> int:
    if num_sources <= 0:
        return 20
    return min(70, 30 + num_sources * 3)


def _generic_insufficient_reason(text: str) -> str:
    return (
        f'The statement claims that "{text}". '
        "Verifying this requires clear and reliable public reporting that directly addresses "
        "the key details of the claim. After reviewing information available online, there is "
        "not enough consistent or specific reporting to confidently confirm or deny it. "
        "Because the available information does not fully establish the facts, the result is "
        "marked as Insufficient."
    )


# -----------------------------
# Main public function
# -----------------------------

def fact_check_with_web(text: str, web_data: list) -> dict:
    """
    Second-pass fact checker using web evidence.
    Generic, non-hardcoded, single-LLM-call, fail-closed.
    """
    cleaned_web = _clean_web_data(web_data)

    try:
        llm = get_llm("qwen2_5")

        prompt = f"""
You are a professional fact-checking system.

STATEMENT:
"{text}"

You are given information that was found publicly online.
Use it ONLY if it is relevant to the statement.

ONLINE INFORMATION:
{json.dumps(cleaned_web, ensure_ascii=False, indent=2)}

TASK (VERY IMPORTANT):
You must do TWO THINGS internally:

1) ANALYZE the relationship between the statement and the information.
   Decide whether the information:
   - supports the statement
   - contradicts the statement
   - is unclear or insufficient

2) Based on that relationship, produce the final verdict.

STRICT RULES:
- Do NOT guess or assume missing facts
- If information clearly contradicts the statement → Incorrect
- If information clearly supports the statement → Correct
- If information is missing, incomplete, or unclear → Insufficient
- Do NOT reverse logic
- Do NOT soften contradictions
- Write explanations for non-technical readers
- Do NOT use phrases like "provided information" or "given data"
- Only include URLs that were actually used in the reasoning

OUTPUT MUST BE STRICT JSON IN THIS EXACT FORMAT:

{{
  "analysis": {{
    "claim_summary": "Brief restatement of what the statement claims",
    "evidence_summary": "Brief summary of what the relevant public information says",
    "relationship": "supports | contradicts | unclear"
  }},
  "final": {{
    "mark": "Correct | Incorrect | Insufficient",
    "confidence": 0-100,
    "reason": "Very long, detailed explanation in plain language",
    "urls": ["list", "of", "relevant", "urls"]
  }}
}}
"""

        response = llm.invoke(prompt)
        parsed = _safe_parse_json(response)

        analysis = parsed.get("analysis", {})
        final = parsed.get("final", {})

        relationship = analysis.get("relationship")
        mark = final.get("mark")
        reason = final.get("reason")
        confidence = final.get("confidence")
        urls = final.get("urls", [])

        if relationship not in ("supports", "contradicts", "unclear"):
            raise ValueError("Invalid relationship")

        if mark not in ("Correct", "Incorrect", "Insufficient"):
            raise ValueError("Invalid mark")

        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("Invalid reason")

        if not isinstance(urls, list):
            urls = []

        # -----------------------------
        # ENFORCE LOGICAL CONSISTENCY
        # -----------------------------
        if relationship == "supports":
            enforced_mark = "Correct"
        elif relationship == "contradicts":
            enforced_mark = "Incorrect"
        else:
            enforced_mark = "Insufficient"

        mark = enforced_mark

        if mark == "Insufficient":
            confidence = _confidence_for_insufficient(len(cleaned_web))
        else:
            if not isinstance(confidence, (int, float)):
                confidence = 85
            confidence = max(0, min(100, int(confidence)))

        reason = _sanitize_reason(reason)
        urls = [u for u in dict.fromkeys(urls) if isinstance(u, str) and u.strip()]

        return {
            "mark": mark,
            "confidence": confidence,
            "reason": reason,
            "urls": urls,
        }

    except Exception:
        return {
            "mark": "Insufficient",
            "confidence": _confidence_for_insufficient(len(cleaned_web)),
            "reason": _generic_insufficient_reason(text),
            "urls": [],
        }
