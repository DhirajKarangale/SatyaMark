# verifyability_with_detailed_reason.py

from typing import Any, Dict
from connect import get_llm
import json


def _safe_parse(output: Any) -> Dict:
    """
    Robustly extract and parse JSON from LLM output.
    Fail-closed to UNVERIFYABLE.
    """
    try:
        # Extract raw content
        if hasattr(output, "content"):
            raw = output.content
        elif isinstance(output, dict):
            raw = output.get("content", "")
        elif isinstance(output, str):
            raw = output
        else:
            raise ValueError("Unknown LLM output type")

        if not isinstance(raw, str):
            raise ValueError("Content is not string")

        raw = raw.strip()

        # Extract JSON object
        start = raw.find("{")
        end = raw.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError("No JSON object found")

        json_text = raw[start : end + 1]
        data = json.loads(json_text)

        mark = data.get("mark")
        confidence = data.get("confidence")
        reason = data.get("reason")

        if mark not in ("VERIFYABLE", "UNVERIFYABLE"):
            raise ValueError("Invalid mark")

        if not isinstance(confidence, int) or not (0 <= confidence <= 100):
            raise ValueError("Invalid confidence")

        if not isinstance(reason, str) or len(reason.strip()) < 60:
            raise ValueError("Reason too short")

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
You are classifying whether a statement ASSERTS an objective factual claim.

You are NOT checking whether the statement is true.
You are ONLY deciding whether it is the kind of statement that COULD be
verified or falsified using external evidence.

Definitions (STRICT):

VERIFYABLE:
- The statement asserts an objective fact about the real world.
- The claim could be checked against external evidence.
- The claim may be TRUE or FALSE.
- Statements about uniquely identifiable or universally known entities
  (such as the Sun, Earth, Moon, gravity, water, planets, physical objects)
  are VERIFYABLE even if incorrect.
- Statements that assert extraordinary, implausible, or controversial facts
  about real-world events (for example: alien involvement, conspiracies,
  supernatural causes, or scientific impossibilities) are STILL VERIFYABLE
  if they clearly claim that something happened in the real world.

UNVERIFYABLE:
- Opinions, preferences, feelings, admiration, inspiration.
- Generic labels, roles, or titles.
- Meaningless or gibberish text.
- Vague or incomplete statements that lack essential identifying details
  where no reasonable person could know what evidence to check.

CRITICAL RULES ABOUT SPECIFICITY:

- If a statement sounds factual BUT does NOT specify enough details for a
  reasonable person to know WHAT evidence to look for, it is UNVERIFYABLE.
- Missing identifiers such as which person, which committee, which proposal,
  which organization, or which event make the statement UNVERIFYABLE.
- HOWEVER, do NOT mark a statement UNVERIFYABLE simply because the claim
  is strange, implausible, controversial, or likely false.
- Do NOT confuse lack of credibility with lack of verifyability.

Explanation requirements:

If the mark is UNVERIFYABLE, your explanation MUST:
- Restate what the statement is claiming in simple words.
- Explain what type of statement it is.
- Clearly explain which critical details are missing.
- Explain why those missing details prevent verification.
- Use very simple, non-technical language.
- Be VERY LONG, VERY DETAILED, and EXPLICIT.

If the mark is VERIFYABLE:
- Briefly explain why the statement is an objective factual claim
  that could be checked against reality.

Confidence score:
- 0 to 100 indicating how confident you are in your classification.

Output STRICTLY valid JSON in this exact format:

{{
  "mark": "VERIFYABLE or UNVERIFYABLE",
  "confidence": number between 0 and 100,
  "reason": "very long, very detailed explanation"
}}

Rules:
- Do NOT add facts.
- Do NOT correct the statement.
- Do NOT use outside knowledge.
- Output ONLY JSON. No extra text.

Text:
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
