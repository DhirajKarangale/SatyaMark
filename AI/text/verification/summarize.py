import re
from typing import List
from html import unescape
from text.utils.huggingface import invoke

NORMALIZATION_MODELS = ["llama3", "mistral", "qwen2_5"]
SUMMARIZATION_MODELS = ["llama3", "mistral", "qwen2_5"]

SEPARATOR = "|#|"

def _clean_input_text(text: str) -> str:
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip()


DATE_PATTERNS = [
    r"\b\d{4}-\d{2}-\d{2}\b",
    r"\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}\b",
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
]
USERNAME_PATTERN = r"^[a-zA-Z0-9_]+$"


def _is_metadata_segment(segment: str) -> bool:
    s = segment.strip()
    if not s:
        return True
    if any(re.search(p, s) for p in DATE_PATTERNS):
        return True
    if re.fullmatch(USERNAME_PATTERN, s):
        return True
    if len(s.split()) <= 4 and not re.search(r"[.!?]", s):
        return True
    return False


def extract_meaningful_chunks(raw_text: str) -> str:
    cleaned = _clean_input_text(raw_text)
    cleaned = re.sub(r"\s*\|\#\|\s*", SEPARATOR, cleaned)

    if SEPARATOR not in cleaned:
        return cleaned

    parts: List[str] = [p.strip() for p in cleaned.split(SEPARATOR) if p.strip()]
    meaningful_parts = [part for part in parts if not _is_metadata_segment(part)]
    return " ".join(meaningful_parts)


# ------------------------------------------------------------------
# Stages
# ------------------------------------------------------------------


def semantic_normalize(text: str) -> str:
    if not text:
        return ""
    prompt = (
        "Perform semantic normalization on the following text.\n\n"
        "- Clean formatting issues.\n"
        "- Remove structural noise.\n"
        "- Preserve meaning and intent.\n"
        "- Do NOT summarize.\n"
        "- Do NOT add new information.\n\n"
        f"Text:\n{text}\n\n"
        "Return ONLY the normalized text without any conversational filler or introductions:"
    )
    try:
        result = invoke(NORMALIZATION_MODELS, prompt, parse_as_json=False)
        return result if result else text
    except Exception:
        return text


def summarize_text(text: str) -> str:
    if not text:
        return ""
    prompt = (
        "Compress the following text into at most 2 sentences.\n"
        "Use ONLY information present in the input.\n"
        "Do NOT add or infer new details.\n\n"
        f"Text:\n{text}\n\n"
        "Return ONLY the compressed summary without any conversational filler, labels, or introductions:"
    )
    try:
        result = invoke(SUMMARIZATION_MODELS, prompt, parse_as_json=False)

        # Clean up any leftover summary formatting just in case
        result = re.sub(r"^compressed summary:\s*", "", result, flags=re.IGNORECASE)
        sentences = re.split(r"(?<=[.!?])\s+", result)
        if len(sentences) > 2:
            result = " ".join(sentences[:2]).strip()

        return result if result else text
    except Exception:
        return text.strip()


def clean_and_summarize(raw_input: str) -> str:
    meaningful = extract_meaningful_chunks(raw_input)
    if not meaningful:
        return ""
    normalized = semantic_normalize(meaningful)
    return summarize_text(normalized)


__all__ = ["clean_and_summarize"]
