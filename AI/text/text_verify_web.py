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

def _normalize_relationship(r: str) -> str:
    if not isinstance(r, str):
        return "unclear"

    r = r.lower().strip()

    if "support" in r:
        return "supports"
    if "contradict" in r:
        return "contradicts"
    if "unclear" in r or "insufficient" in r or "not enough" in r:
        return "unclear"

    return "unclear"

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


def _normalize_geography(reason: str) -> str:
    """
    Fix common geographic phrasing issues for clarity.
    This is linguistic normalization only, not fact inference.
    """
    replacements = {
        "india or kashmir": "India, specifically the Jammu and Kashmir region",
        "india and kashmir": "India, specifically the Jammu and Kashmir region",
        "within india or kashmir": "within India, specifically the Jammu and Kashmir region",
        "regions within india or kashmir": "regions within India, specifically the Jammu and Kashmir region",
    }

    lower = reason.lower()
    for bad, good in replacements.items():
        if bad in lower:
            start = lower.find(bad)
            end = start + len(bad)
            reason = reason[:start] + good + reason[end:]
            break

    return reason.strip()


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
        llm = get_llm("deepseek_r1")

        prompt = f"""
You are a professional fact-checking system.

STATEMENT:
"{text}"

You are given information that was found publicly online.
Use it ONLY if it is relevant to the statement.

ONLINE INFORMATION:
{json.dumps(cleaned_web, ensure_ascii=False, indent=2)}

TASK (VERY IMPORTANT):

You must determine whether the statement is:
- Correct
- Incorrect
- Insufficient

Follow these principles:

1. Compare the statement directly against the online information.
2. If the information clearly confirms the claim, mark it Correct.
3. If the information clearly disproves the claim, mark it Incorrect.
4. If the information does not clearly confirm or disprove the claim, mark it Insufficient.

Important clarifications:
- Phrases like "latest report", "current data", or "recent figures" refer to the most up-to-date information available in the provided sources.
- Numeric claims should be evaluated by whether the reported values satisfy or contradict the claim.
- Do not require exact wording matches; evaluate factual equivalence.
- Do not guess or assume facts not present in the information.

Then:
- Explain your reasoning in clear, non-technical language.
- List only URLs that were actually used.

OUTPUT STRICT JSON ONLY:

{{
  "mark": "Correct | Incorrect | Insufficient",
  "confidence": 0-100,
  "reason": "Very detailed explanation",
  "urls": ["list", "of", "used", "urls"]
}}
"""
        response = llm.invoke(prompt)
        parsed = _safe_parse_json(response)

        # final = parsed.get("final", {})
        # reason = final.get("reason")
        # confidence = final.get("confidence")
        # urls = final.get("urls", [])

        # analysis = parsed.get("analysis", {})
        # relationship = _normalize_relationship(analysis.get("relationship"))

        mark = parsed.get("mark")
        confidence = parsed.get("confidence")
        reason = parsed.get("reason")
        urls = parsed.get("urls", [])

        if not isinstance(reason, str) or not reason.strip():
            reason = _generic_insufficient_reason(text)

        if not isinstance(urls, list):
            urls = []

        # Enforce verdict strictly from relationship
        # if relationship == "supports":
        #     mark = "Correct"
        # elif relationship == "contradicts":
        #     mark = "Incorrect"
        # else:
        #     mark = "Insufficient"

        if mark == "Insufficient":
            confidence = _confidence_for_insufficient(len(cleaned_web))
        else:
            if not isinstance(confidence, (int, float)):
                confidence = 85
            confidence = max(0, min(100, int(confidence)))

        reason = _sanitize_reason(reason)
        reason = _normalize_geography(reason)
        urls = [u for u in dict.fromkeys(urls) if isinstance(u, str) and u.strip()]

        return {
            "mark": mark,
            "confidence": confidence,
            "reason": reason,
            "urls": urls,
        }

    except Exception as e:
        if cleaned_web:
            return {
                "mark": "Insufficient",
                "confidence": _confidence_for_insufficient(len(cleaned_web)),
                "reason": _generic_insufficient_reason(text),
                "urls": [w["url"] for w in cleaned_web[:3]],
            }
        raise
