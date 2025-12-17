# verifyability_checker.py

from typing import Optional, Any
from connect import get_llm


def _safe_extract(output: Any) -> str:
    """
    Extract VERIFYABLE / UNVERIFYABLE from LLM output.
    Supports ChatMessage, dict, or raw string.
    Fail-closed.
    """
    if output is None:
        return "UNVERIFYABLE"

    # LangChain ChatMessage
    if hasattr(output, "content"):
        text = output.content
    # Dict-like
    elif isinstance(output, dict):
        text = output.get("content")
    # Raw string
    elif isinstance(output, str):
        text = output
    else:
        return "UNVERIFYABLE"

    if not isinstance(text, str):
        return "UNVERIFYABLE"

    value = text.strip().upper()
    if value == "VERIFYABLE":
        return "VERIFYABLE"
    if value == "UNVERIFYABLE":
        return "UNVERIFYABLE"

    return "UNVERIFYABLE"


def check_verifyability(text: str) -> str:
    """
    LLM-only claim-type classification.
    Returns VERIFYABLE or UNVERIFYABLE.
    """
    try:
        llm = get_llm("qwen2_5")

        prompt = f"""
You are classifying the TYPE of statement.

You are NOT checking whether the statement is true.
You are ONLY deciding whether it ASSERTS an objective factual claim.

VERIFYABLE:
- Asserts a concrete, objective fact.
- Could be checked using external evidence.
- May be true OR false.

UNVERIFYABLE:
- Opinions, preferences, feelings.
- Generic roles or labels.
- Commands, questions, incomplete or meaningless text.

Rules:
- Do NOT judge correctness.
- Do NOT add facts.
- Decide ONLY whether the claim is objectively checkable.

Examples:
"The Eiffel Tower is located in Germany" → VERIFYABLE
"I like mangoes" → UNVERIFYABLE

Output EXACTLY one word:
VERIFYABLE
or
UNVERIFYABLE

Text:
{text}
""".strip()

        response = llm.invoke(prompt)
        return _safe_extract(response)

    except Exception:
        return "UNVERIFYABLE"
