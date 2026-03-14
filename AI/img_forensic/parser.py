import re
import json
from typing import Dict, Any


def clean_text(raw_text: Any) -> str:
    if hasattr(raw_text, "content"):
        text = raw_text.content
    elif isinstance(raw_text, dict) and "content" in raw_text:
        text = raw_text.get("content", "")
    else:
        text = str(raw_text)

    if not isinstance(text, str):
        return ""

    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"</?think>", "", text, flags=re.IGNORECASE)

    return text.strip()


def extract_json(raw_text: Any) -> Dict[str, Any]:
    """Cleans text and securely extracts a JSON object."""
    cleaned = clean_text(raw_text)

    cleaned = re.sub(r"```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end <= start:
        if "UNVERIFYABLE" in cleaned.upper():
            return {
                "mark": "UNVERIFYABLE",
                "confidence": 100,
                "reason": "Extracted from raw text.",
            }
        elif "VERIFYABLE" in cleaned.upper():
            return {
                "mark": "VERIFYABLE",
                "confidence": 100,
                "reason": "Extracted from raw text.",
            }

        raise ValueError(
            "No JSON object found in the model output. Output was: " + cleaned[:100]
        )

    json_string = cleaned[start : end + 1]

    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode JSON: {e}")
