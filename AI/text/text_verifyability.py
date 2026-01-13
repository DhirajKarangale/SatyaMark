from typing import Any, Dict
from connect import get_llm
import json

_PREFERRED_MODELS = ["deepseek_r1", "minicheck", "bart_large_cnn", "flan_t5_xl"]


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
        prompt = f"""
You classify a statement based ONLY on whether it can be FACT-CHECKED
using independent, external evidence.

You are NOT judging truth or accuracy.
You are NOT assuming access to private records, self-reports, or personal testimony.

A claim must be realistically checkable by an independent verifier
to be considered VERIFYABLE.

====================
DEFINITIONS
====================

A statement is VERIFYABLE if:
- It asserts an objective claim about the real world
AND
- There exists a realistic way for an independent party to check it using
  public records, scientific measurement, historical documentation,
  physical inspection, or widely accessible evidence.
- The claim does NOT rely solely on a person's private actions,
  internal records, or self-reporting.
- Claims about public events, known facts, physical properties,
  scientific phenomena, or documented history are VERIFYABLE.

Examples:
- "Water boils at 100°C at sea level." → VERIFYABLE
- "The Eiffel Tower is in Paris." → VERIFYABLE
- "COVID-19 vaccines were approved in 2020." → VERIFYABLE

A statement is UNVERIFYABLE if:
- It describes a private personal action, habit, or behavior
  that cannot be independently verified.
- It is a personal feeling, preference, belief, or opinion.
- It refers to internal mental states.
- It lacks sufficient identifiers to locate evidence.
- It is abstract, philosophical, or subjective.

Examples:
- "I eat bread at night." → UNVERIFYABLE
- "I drank coffee yesterday." → UNVERIFYABLE
- "I like apples." → UNVERIFYABLE
- "He won an award." → UNVERIFYABLE (unclear subject)

====================
IMPORTANT RULE
====================

If no realistic external fact-checking path exists,
the statement MUST be classified as UNVERIFYABLE.

Do NOT classify something as VERIFYABLE merely because it could be
observed in theory or under hypothetical surveillance.

====================
OUTPUT FORMAT
====================

Output STRICT JSON ONLY:

{{
  "mark": "VERIFYABLE or UNVERIFYABLE",
  "confidence": number between 0 and 100,
  "reason": "very long, detailed explanation"
}}

No extra text.
No markdown.
No commentary.

====================
STATEMENT
====================

{text}
""".strip()

        for model_name in _PREFERRED_MODELS:
            try:
                llm = get_llm(model_name)
                response = llm.invoke(prompt)
                result = _safe_parse(response)

                if result and result.get("mark"):
                    return result

            except Exception:
                continue

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
