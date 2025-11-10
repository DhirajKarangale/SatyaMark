
# text_summarize.py
from typing import Any, Optional

# Optional: pip install langdetect
try:
    from langdetect import detect  # type: ignore
except Exception:
    detect = None

from connect import get_llm


def _extract_text(output: Any) -> str:
    """
    Normalize LLM outputs (AIMessage, dict, or str) into a clean string.
    Works with LangChain chat models that return AIMessage(content=...).
    """
    # LangChain AIMessage-like
    if hasattr(output, "content"):
        return (output.content or "").strip()

    # Generic dict containing 'content'
    if isinstance(output, dict) and "content" in output:
        return (output.get("content") or "").strip()

    # Fallback to string conversion
    return (str(output) if output is not None else "").strip()


def _looks_english(text: str) -> bool:
    """
    Prefer langdetect when available; fallback to a simple ASCII/Latin heuristic.
    Mirrors the behavior used in your CLI file.
    """
    if detect:
        try:
            return detect(text) == "en"
        except Exception:
            pass  # fall through to heuristic if detection fails

    # Heuristic: if most alphabetic characters are basic Latin, assume English.
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return True
    ascii_letters = [c for c in letters if ord(c) < 128]
    return (len(ascii_letters) / max(1, len(letters))) > 0.92


def summarize_text(text: str, *, enforce_english: bool = True) -> str:
    """
    Summarize any text (multilingual) into short, simple English.

    Ports the key behaviors from your CLI version:
      - Prompting: strong system-like instructions + few-shot (non-English → English)
      - English enforcement: optional one-shot rewrite only if needed
      - Safety/Fidelity: do NOT add new facts; keep key numbers/names/dates
      - Output format control: 4–7 bullets + 2–3 sentence gist

    Args:
        text: Input text to summarize.
        enforce_english: If True, auto-rewrite once if the first pass isn't English.

    Returns:
        Summarized text as a string.
    """
    llm = get_llm("llama3")  # Should return a chat/instruct-capable model with .invoke()

    # ---- Prompting (system-like + few-shot) ----
    system_msg = (
        "You are a professional summarizer.\n\n"
        "CRITICAL REQUIREMENTS:\n"
        "- ALWAYS respond in ENGLISH ONLY, regardless of the input language.\n"
        "- If the input is not in English, first infer/translate the important content into English,\n"
        "  then write the summary in plain, simple English.\n"
        "- Do NOT include any non-English words in the output (no code-switching).\n"
        "- Do NOT add new facts beyond what is provided.\n"
        "- Prefer short sentences, everyday words, and neutral tone.\n"
        "- Keep key numbers, names, and dates when relevant.\n\n"
        "OUTPUT FORMAT:\n"
        "1) 4–7 bullet points with the key facts.\n"
        "2) A short 2–3 sentence paragraph with the overall gist."
    )

    # Few-shot example: Non-English input → English output
    fewshot_user = (
        "User:\n"
        "Résumé (français): « Le rapport explique la baisse des ventes au T2 et propose trois actions pour le T3. »"
    )
    fewshot_assistant = (
        "Assistant:\n"
        "- The report analyzes lower sales in Q2.\n"
        "- It lists three actions planned for Q3 to improve results.\n"
        "- The focus is on operational fixes and marketing.\n\n"
        "Overall: The document explains why Q2 sales fell and outlines three practical steps intended to boost performance in Q3."
    )

    human_msg = f"User:\n[text to summarize starts]\n{text}\n[text to summarize ends]"

    # Compose a single prompt string that simulates system + chat turns
    prompt = (
        f"SYSTEM:\n{system_msg}\n\n"
        f"{fewshot_user}\n\n"
        f"{fewshot_assistant}\n\n"
        f"{human_msg}\n\n"
        "Assistant:\n"
    )

    # ---- First pass ----
    first_raw = llm.invoke(prompt)
    summary = _extract_text(first_raw)

    # ---- English enforcement (optional single retry) ----
    if enforce_english and not _looks_english(summary):
        force_prompt = (
            "SYSTEM:\n"
            "Rewrite the following draft into PLAIN, SIMPLE ENGLISH ONLY.\n"
            "Do NOT add or remove facts. Maintain the exact OUTPUT FORMAT:\n"
            "1) 4–7 bullet points with the key facts.\n"
            "2) A short 2–3 sentence paragraph with the overall gist.\n\n"
            "Draft:\n"
            f"{summary}\n\n"
            "Assistant:\n"
        )
        forced_raw = llm.invoke(force_prompt)
        summary = _extract_text(forced_raw)

    return summary


__all__ = ["summarize_text"]
