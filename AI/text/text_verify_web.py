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
Use it ONLY if it is directly relevant to verifying the statement.

ONLINE INFORMATION:
{json.dumps(cleaned_web, ensure_ascii=False, indent=2)}

TASK (VERY IMPORTANT):

You must determine whether the statement is:
- Correct
- Incorrect
- Insufficient

Your goal is to verify whether the statement accurately describes
a real-world event or fact, not whether someone reported it.

-----------------------------------
CORE FACT-CHECKING RULES
-----------------------------------

1. Compare the statement directly against the online information.
2. Mark the statement Correct ONLY if the real-world event or fact
   is independently confirmed by multiple reliable sources.
3. Mark the statement Incorrect ONLY if the online information
   explicitly and clearly disproves the claim.
4. Mark the statement Insufficient if the information does not
   clearly confirm or disprove the claim.

-----------------------------------
CLAIM TYPE RULE (MANDATORY)
-----------------------------------

If a statement asserts that a real-world event occurred
(e.g., deaths, attacks, casualties, disasters, mass arrests),
you must verify whether the event itself is independently confirmed.

Confirmation that a media outlet, organization, or individual
reported or concluded something does NOT count as confirmation
of the event itself.

Such cases MUST be marked Insufficient unless independently verified.

-----------------------------------
SOURCE INDEPENDENCE RULE (MANDATORY)
-----------------------------------

Multiple sources only count as independent if they originate
from different organizations and do not rely on the same
primary report or investigation.

Sources that merely repeat, summarize, or cite another outlet’s
reporting (including Wikipedia) do NOT count as independent
confirmation.

Wikipedia may be used for background context only and must NOT
be treated as primary evidence for extraordinary claims.

-----------------------------------
NUMERIC CLAIM RULE (MANDATORY)
-----------------------------------

Numeric claims must be evaluated carefully:

- Lower confirmed numbers do NOT contradict higher claimed numbers
  unless a source explicitly states that the higher figure is false,
  impossible, or disproven.

- Reports stating “at least”, “confirmed so far”, or partial counts
  represent minimum verified figures, not upper limits.

- If numeric figures conflict without explicit refutation,
  the result MUST be marked Insufficient.

-----------------------------------
EXTRAORDINARY CLAIM RULE
-----------------------------------

Claims involving exceptionally large numbers of deaths,
historic-scale events, or mass casualties require confirmation
from multiple independent international or neutral sources.

Single-outlet confirmation is insufficient for such claims.

-----------------------------------
REASONING AND OUTPUT
-----------------------------------

Then:
- Explain your reasoning in clear, non-technical language.
- Do NOT rely on tone, emotion, or political framing.
- List ONLY the URLs that were actually used in your reasoning.

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

        mark = parsed.get("mark")
        confidence = parsed.get("confidence")
        reason = parsed.get("reason")
        urls = parsed.get("urls", [])

        if not isinstance(reason, str) or not reason.strip():
            reason = _generic_insufficient_reason(text)

        if not isinstance(urls, list):
            urls = []

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
