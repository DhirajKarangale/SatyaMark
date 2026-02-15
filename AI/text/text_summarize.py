import re
from typing import Any, List
from html import unescape

from connect import get_llm

_PREFERRED_MODELS = ["flan_t5_xl", "bart_large_cnn", "minicheck"]

SEPARATOR = "|#|"


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _extract_text(output: Any) -> str:
    if hasattr(output, "content"):
        return (output.content or "").strip()
    if isinstance(output, dict) and "content" in output:
        return (output.get("content") or "").strip()
    return (str(output) if output is not None else "").strip()


def _clean_summary_output(text: str) -> str:
    if not isinstance(text, str):
        return ""

    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"^compressed summary:\s*", "", text, flags=re.IGNORECASE)

    # Hard remove separator if somehow leaked
    text = text.replace(SEPARATOR, " ")

    text = re.sub(r"\s+", " ", text).strip()

    sentences = re.split(r"(?<=[.!?])\s+", text)
    if len(sentences) > 2:
        text = " ".join(sentences[:2]).strip()

    return text


def _clean_input_text(text: str) -> str:
    if not text:
        return ""

    text = unescape(text)

    # Remove HTML
    text = re.sub(r"<[^>]+>", " ", text)

    # Normalize weird whitespace including non-breaking spaces
    text = text.replace("\u00A0", " ")
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ------------------------------------------------------------------
# Deterministic Metadata Filtering
# ------------------------------------------------------------------

DATE_PATTERNS = [
    r"\b\d{4}-\d{2}-\d{2}\b",
    r"\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}\b",
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
]

USERNAME_PATTERN = r"^[a-zA-Z0-9_]+$"


def _is_date(text: str) -> bool:
    return any(re.search(p, text) for p in DATE_PATTERNS)


def _is_metadata_segment(segment: str) -> bool:
    s = segment.strip()

    if not s:
        return True

    if _is_date(s):
        return True

    if re.fullmatch(USERNAME_PATTERN, s):
        return True

    # Remove short title-like fragments without punctuation
    if len(s.split()) <= 4 and not re.search(r"[.!?]", s):
        return True

    return False


def extract_meaningful_chunks(raw_text: str) -> str:
    cleaned = _clean_input_text(raw_text)

    # Normalize separator spacing aggressively
    cleaned = re.sub(r"\s*\|\#\|\s*", SEPARATOR, cleaned)

    if SEPARATOR not in cleaned:
        return cleaned

    parts: List[str] = [p.strip() for p in cleaned.split(SEPARATOR) if p.strip()]

    meaningful_parts = [
        part for part in parts if not _is_metadata_segment(part)
    ]

    return " ".join(meaningful_parts)


# ------------------------------------------------------------------
# Stage 1: Semantic Normalization (NO summarization)
# ------------------------------------------------------------------

def semantic_normalize(text: str) -> str:
    if not text:
        return ""

    prompt = (
        "Perform semantic normalization.\n\n"
        "- Clean formatting issues.\n"
        "- Remove structural noise.\n"
        "- Preserve meaning and intent.\n"
        "- Do NOT summarize.\n"
        "- Do NOT add new information.\n\n"
        f"Text:\n{text}\n\n"
        "Normalized text:"
    )

    for model_name in _PREFERRED_MODELS:
        try:
            llm = get_llm(model_name)
            out = llm.invoke(prompt)
            result = _extract_text(out)
            if result:
                return result.strip()
        except Exception:
            continue

    return text


# ------------------------------------------------------------------
# Stage 2: Summarization
# ------------------------------------------------------------------

def summarize_text(text: str) -> str:
    if not text:
        return ""

    prompt = (
        "Compress the following text into at most 2 sentences.\n"
        "Use ONLY information present in the input.\n"
        "Do NOT add or infer new details.\n\n"
        f"Text:\n{text}\n\n"
        "Compressed summary:"
    )

    for model_name in _PREFERRED_MODELS:
        try:
            llm = get_llm(model_name)
            out = llm.invoke(prompt)
            raw = _extract_text(out)
            result = _clean_summary_output(raw)
            if result:
                return result
        except Exception:
            continue

    return text.strip()


# ------------------------------------------------------------------
# Public Pipeline
# ------------------------------------------------------------------

def clean_and_summarize(raw_input: str) -> str:
    meaningful = extract_meaningful_chunks(raw_input)

    if not meaningful:
        return ""

    normalized = semantic_normalize(meaningful)

    return summarize_text(normalized)


__all__ = ["clean_and_summarize"]
