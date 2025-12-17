# verifyability_with_detailed_reason.py

from typing import Any, Dict
from connect import get_llm
import json


def _safe_parse(output: Any) -> Dict:
    """
    Safely parse strict JSON output from the LLM.
    Fail-closed to UNVERIFYABLE with a detailed fallback reason.
    """
    try:
        if hasattr(output, "content"):
            text = output.content
        elif isinstance(output, dict):
            text = output.get("content")
        elif isinstance(output, str):
            text = output
        else:
            raise ValueError("Unknown LLM output type")

        data = json.loads(text)

        mark = data.get("mark")
        confidence = data.get("confidence")
        reason = data.get("reason")

        if mark not in ("VERIFYABLE", "UNVERIFYABLE"):
            raise ValueError("Invalid mark")

        if not isinstance(confidence, int) or not (0 <= confidence <= 100):
            raise ValueError("Invalid confidence")

        if not isinstance(reason, str) or len(reason.strip()) < 80:
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
                "The statement could not be reliably evaluated because it does not "
                "clearly present enough specific information to determine whether it "
                "asserts an objective, externally checkable fact. As a safety measure, "
                "it is treated as unverifyable."
            ),
        }


def check_verifyability(text: str) -> Dict:
    """
    LLM-only verifyability classification with very deep explanation
    and strict handling of vague or underspecified factual claims.
    """
    try:
        llm = get_llm("qwen2_5")

        prompt = f"""
You are explaining statement verifyability to NON-TECHNICAL users.

Your task is NOT to check whether a statement is true.
Your task is to decide whether the statement ASSERTS an objective factual claim
that could reasonably be checked using external evidence.

Definitions:

VERIFYABLE:
- The statement asserts a concrete, objective fact.
- The statement contains enough specific information for a reasonable person
  to know WHAT evidence to look for.
- The claim may be true OR false.

UNVERIFYABLE:
- Opinions, preferences, feelings, admiration, or inspiration.
- Generic roles, labels, or titles.
- Meaningless or gibberish text.
- Vague or incomplete statements that lack critical identifying details.

CRITICAL REQUIREMENT (VERY IMPORTANT):

- If a statement sounds factual BUT does NOT clearly specify key details
  (such as which person, organization, committee, proposal, event, place, or time),
  it MUST be classified as UNVERIFYABLE.
- Generic phrases like "the committee", "the proposal", "they", or "it"
  without clear identification make the statement UNVERIFYABLE,
  because no one would know what evidence to check.

Explanation requirements (MANDATORY for UNVERIFYABLE):

If the mark is UNVERIFYABLE, your explanation MUST:
- Clearly restate what the statement is claiming in simple words.
- Explain that the statement is missing important details.
- Explain exactly which kinds of details are missing.
- Explain why, without those details, the claim cannot be checked or confirmed.
- Use very simple, everyday language.
- Be VERY LONG, VERY DETAILED, and VERY EXPLICIT.
- It is acceptable if the explanation is repetitive, as long as it is clear.

If the mark is VERIFYABLE:
- Briefly explain why the statement is a factual claim that could be checked.

Confidence score:
- 0–100 indicating how confident you are in the classification.
- Use high confidence when the case is clear.

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
                "The system encountered an internal error while analyzing the statement. "
                "Because it could not reliably determine whether the text asserts a "
                "specific, externally checkable fact, the statement is treated as "
                "unverifyable to avoid providing misleading results."
            ),
        }
