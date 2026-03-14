import json
from typing import List, Dict, Any
from text.utils.huggingface import invoke

MODELS = ["deepseek_r1", "deepseek_v3", "qwen2_5"]

FORBIDDEN_PHRASES = (
    "provided web evidence",
    "provided web information",
    "given data",
    "given evidence",
    "provided data",
    "provided information",
    "based on the text",
)


def _sanitize_reason(reason: str) -> str:
    """Removes robotic LLM phrasing to make the reasoning sound like a human journalist."""
    r = reason
    for phrase in FORBIDDEN_PHRASES:
        r = r.replace(phrase, "publicly reported information")
    return r.strip()


def fact_check(statement: str, web_data: List[Dict[str, Any]]) -> dict:
    # 1. Define the fallback response so we don't have to type it multiple times
    fallback_response = {
        "mark": "Insufficient",
        "confidence": 30,
        "reason": "The system could not confidently process the verification data or insufficient data was provided.",
        "urls": [],
    }

    # 2. THE NEW CHECK: If the statement is empty or we have absolutely no web data
    if not statement or not str(statement).strip() or not web_data:
        print(
            "[Warning] Missing statement or web data. Returning default insufficient response."
        )
        return fallback_response

    # 3. Filter out empty data before sending to LLM
    valid_evidence = [item for item in web_data if len(item.get("data", "")) > 50]

    # 4. SECONDARY CHECK: If all data was filtered out (meaning no useful text was scraped)
    if not valid_evidence:
        print(
            "[Warning] No valid evidence remained after filtering. Returning default insufficient response."
        )
        return fallback_response

    prompt = f"""
You are a professional fact-checking system. 

STATEMENT TO VERIFY:
"{statement}"

EVIDENCE GATHERED FROM THE WEB:
{json.dumps(valid_evidence, ensure_ascii=False, indent=2)}

TASK:
1. Compare the statement against the evidence. 
2. Ignore any evidence that is irrelevant (like author biographies).
3. Determine whether the statement is Correct, Incorrect, or Insufficient.
   - Mark Correct if the core of the statement is confirmed by the evidence.
   - Mark Incorrect if the evidence explicitly disproves the statement.
   - Mark Insufficient if there isn't enough info to make a call.

OUTPUT STRICT JSON ONLY. Do not use Markdown formatting blocks (like ```json).
{{
  "mark": "Correct | Incorrect | Insufficient",
  "confidence": <integer between 0 and 100>,
  "reason": "<Detailed explanation of the reality based on the evidence. Do not say 'The evidence says...'>",
  "urls": ["<list>", "<of>", "<urls>", "<actually>", "<used>", "<in>", "<your>", "<reasoning>"]
}}
"""
    try:
        # Assuming your invoke function handles forcing the JSON output
        parsed = invoke(MODELS, prompt, parse_as_json=True)

        # Clean up the reasoning text
        if "reason" in parsed and isinstance(parsed["reason"], str):
            parsed["reason"] = _sanitize_reason(parsed["reason"])

        return parsed

    except Exception as e:
        print(f"[Error] Verification failed: {e}")
        return fallback_response
