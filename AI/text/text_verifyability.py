# verifyability_with_detailed_reason.py

from typing import Any, Dict
from connect import get_llm
import json


def _safe_parse(output: Any) -> Dict:
    try:
        if hasattr(output, "content"):
            raw = output.content
        elif isinstance(output, dict):
            raw = output.get("content", "")
        elif isinstance(output, str):
            raw = output
        else:
            raise ValueError()

        if not isinstance(raw, str):
            raise ValueError()

        raw = raw.strip()
        start = raw.find("{")
        end = raw.rfind("}")

        if start == -1 or end == -1:
            raise ValueError()

        data = json.loads(raw[start : end + 1])

        # Normalize mark
        mark = data.get("mark")
        if not isinstance(mark, str):
            raise ValueError()
        mark = mark.upper()
        if mark not in ("VERIFYABLE", "UNVERIFYABLE"):
            raise ValueError()

        # Normalize confidence
        confidence_raw = data.get("confidence")
        confidence = int(float(confidence_raw))
        if not (0 <= confidence <= 100):
            raise ValueError()

        # Check reason
        reason = data.get("reason")
        if not isinstance(reason, str) or len(reason.strip()) < 60:
            raise ValueError()

        return {
            "mark": mark,
            "confidence": confidence,
            "reason": reason.strip(),
        }

    except Exception:
        return {
            "mark": "UNVERIFYABLE",
            "confidence": 100,
            "reason": (
                "The system could not reliably interpret the model output as a valid "
                "structured response. To avoid returning misleading information, the "
                "statement is treated as unverifyable."
            ),
        }


def check_verifyability(text: str) -> Dict:
    """
    LLM-only verifyability classification with deep explanation.
    """
    try:
        llm = get_llm("qwen2_5")

        prompt = f"""
You classify a statement based only on whether it ASSERTS an objective factual claim.

You are NOT judging truth or accuracy.
You are ONLY deciding whether the statement COULD, in principle, be verified or falsified using external evidence.

====================
DEFINITIONS
====================

A statement is VERIFYABLE if:
- It asserts an objective claim about the real world.
- The claim could be checked using scientific, historical, physical, or observable evidence.
- It may be TRUE or FALSE; accuracy does not matter.
- Claims about physical objects, places, biological species, products, or natural phenomena are VERIFYABLE.
- Claims comparing physical characteristics (taste, color, size, weight, composition, etc.) are VERIFYABLE because they can be tested.
  Example: "Apples taste the same as mangoes." → VERIFYABLE.
- Extraordinary or controversial claims are VERIFYABLE if they assert that something happened in the real world.

A statement is UNVERIFYABLE if:
- It is a personal feeling, preference, belief, or opinion.
  Examples: "I like apples.", "Mangoes taste better."
- It relies on subjective evaluation instead of objective comparison.
- It is too vague to test because it lacks essential identifiers required to locate evidence when the subject is a person, organization, or event.
  Examples: "He won the award." (which person?)
- It is purely abstract, metaphorical, or philosophical.
- It is meaningless, nonsensical, or gibberish.

====================
SPECIFICITY RULE
====================

Specificity is required ONLY for claims about:
- individuals
- organizations
- events

Generic categories of physical objects (e.g., fruits, animals, chemicals, planets) do NOT require further specificity to be VERIFYABLE.

====================
EXPLANATION REQUIREMENTS
====================

If UNVERIFYABLE:
- Provide a long, simple-language explanation describing why the claim cannot be objectively checked.

If VERIFYABLE:
- Provide a detailed explanation describing why the claim could be tested in the real world.

====================
OUTPUT FORMAT
====================

Output STRICT JSON:

{{
  "mark": "VERIFYABLE or UNVERIFYABLE",
  "confidence": number between 0 and 100,
  "reason": "very long, detailed explanation"
}}

No extra text outside the JSON.
No commentary.
No markdown.
No corrections of the statement.

====================
STATEMENT
====================

{text}
""".strip()

        response = llm.invoke(prompt)
        return _safe_parse(response)

    except Exception:
        return {
            "mark": "UNVERIFYABLE",
            "confidence": 100,
            "reason": (
                "An internal error occurred while processing the statement. Because the "
                "system could not reliably determine whether the text asserts an "
                "objectively checkable factual claim, it is treated as unverifyable."
            ),
        }
