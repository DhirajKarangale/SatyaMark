import re
from typing import Any, List
from html import unescape

try:
    from langdetect import detect
except Exception:
    detect = None

from connect import get_llm


def _extract_text(output: Any) -> str:
    if hasattr(output, "content"):
        return (output.content or "").strip()
    if isinstance(output, dict) and "content" in output:
        return (output.get("content") or "").strip()
    return (str(output) if output is not None else "").strip()


def _split_sentences(text: str) -> List[str]:
    sents = re.split(r"(?<=[\.\!\?])\s+", text.strip())
    return [s.strip() for s in sents if s.strip()]


def _looks_english(text: str) -> bool:
    if detect:
        try:
            return detect(text) == "en"
        except Exception:
            pass
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return True
    ascii_letters = [c for c in letters if ord(c) < 128]
    return (len(ascii_letters) / max(1, len(letters))) > 0.92


def _clean_input_text(text: str) -> str:
    """
    Clean all formatting (HTML, markdown, bullets, links, emojis).
    Keep only readable text.
    """
    if not text:
        return ""

    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[*_`~]+", " ", text)
    text = re.sub(r"\b\/i\b", " ", text)
    text = re.sub(r"^[\-\*\•\·]\s*", " ", text, flags=re.MULTILINE)
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[@#]\w+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def normalize_meaning(text: str) -> str:
    """
    Convert noisy, broken, or tag-contaminated text into clean,
    meaning-preserving English. Ensures stable semantic input.
    """
    cleaned = _clean_input_text(text)
    llm = get_llm("llama3")

    prompt = (
        "Rewrite the following text into clean, correct, plain English WITHOUT changing "
        "any facts, meaning, numbers, names, or implications. Fix broken formatting tags, "
        "correct partial markup, and repair awkward or incomplete wording. "
        "Do NOT summarize. Maintain full meaning.\n\n"
        f"Text:\n{cleaned}\n\n"
        "Clean rewrite:"
    )

    out = llm.invoke(prompt)
    normalized = _extract_text(out).strip()
    return normalized


def summarize_text(text: str, *, enforce_english: bool = True) -> str:
    """
    Summarize input text into a short, meaning-based gist (up to 2 sentences).

    - First, normalize meaning so different wording gives same summary.
    - Then produce a stable semantic summary.
    - No new facts.
    """

    normalized = normalize_meaning(text)

    llm = get_llm("llama3")

    system_msg = (
        "You are a professional factual summarizer.\n"
        "Summarize the meaning only — not the wording.\n"
        "If two texts mean the same, your summary must be identical.\n"
        "Do NOT add new facts. Keep a neutral tone.\n"
        "Max 2 sentences. No bullets or headings."
    )

    human_msg = f"Text to summarize:\n{normalized}"

    prompt = "\n\n".join(
        [f"SYSTEM:\n{system_msg}", f"User:\n{human_msg}", "Assistant:"]
    )

    raw = llm.invoke(prompt)
    summary = _extract_text(raw).strip()

    if enforce_english and not _looks_english(summary):
        force_prompt = (
            "Rewrite the following summary in plain, simple English (max 2 sentences):\n\n"
            f"{summary}"
        )
        forced = llm.invoke(force_prompt)
        summary = _extract_text(forced).strip()

    sents = _split_sentences(summary)
    return " ".join(sents[:2]).strip()


__all__ = ["summarize_text", "normalize_meaning"]
