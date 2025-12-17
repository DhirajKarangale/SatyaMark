import time
from huggingface_hub.utils import HfHubHTTPError
import re
from typing import Any, List
from html import unescape

try:
    from langdetect import detect
except Exception:
    detect = None

from connect import get_llm


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _extract_text(output: Any) -> str:
    if hasattr(output, "content"):
        return (output.content or "").strip()
    if isinstance(output, dict) and "content" in output:
        return (output.get("content") or "").strip()
    return (str(output) if output is not None else "").strip()


def _split_sentences(text: str) -> List[str]:
    sents = re.split(r"(?<=[.!?])\s+", text.strip())
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


# ------------------------------------------------------------------
# Low-level text cleaning (NO LLM)
# ------------------------------------------------------------------

def _clean_input_text(text: str) -> str:
    if not text:
        return ""

    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[*_`~]+", " ", text)
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[@#]\w+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ------------------------------------------------------------------
# Rule-based noise detection
# ------------------------------------------------------------------

DATE_PATTERNS = [
    r"\b\d{4}-\d{2}-\d{2}\b",
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    r"\bInvalid Date\b",
]

USERNAME_PATTERN = r"^[a-zA-Z0-9_]{2,20}$"


def _is_noise_segment(seg: str) -> bool:
    s = seg.strip()
    if not s:
        return True

    for p in DATE_PATTERNS:
        if re.search(p, s):
            return True

    if re.fullmatch(USERNAME_PATTERN, s):
        return True

    # Tag lists (comma-separated, short)
    if "," in s and len(s.split()) <= 6:
        return True

    # Too short → usually title / label
    if len(s) < 40:
        return True

    return False


def extract_core_content(raw: str) -> str:
    parts = [p.strip() for p in raw.split("||satyamark seperator||")]
    meaningful = [p for p in parts if not _is_noise_segment(p)]
    return " ".join(meaningful)


# ------------------------------------------------------------------
# LLM-assisted semantic pruning (NO summarization)
# ------------------------------------------------------------------

def semantic_prune(text: str) -> str:
    llm = get_llm("qwen2_5")

    prompt = (
        "Extract ONLY the sentences that contain the main informational or opinion content.\n"
        "DO NOT add, infer, expand, or rewrite anything.\n"
        "DO NOT introduce titles, examples, or background knowledge.\n"
        "Return ONLY text that appears verbatim or near-verbatim in the input.\n\n"
        f"Text:\n{text}\n\n"
        "Extracted content:"
    )

    out = llm.invoke(prompt)
    return _extract_text(out)

# ------------------------------------------------------------------
# Meaning normalization (stable semantic input)
# ------------------------------------------------------------------

def normalize_meaning(text: str) -> str:
    cleaned = _clean_input_text(text)

    llm = get_llm("qwen2_5")

    prompt = (
        "Rewrite the following text into clean, correct English without changing "
        "any facts, names, numbers, or meaning.\n"
        "Fix grammar and broken formatting.\n"
        "Do NOT summarize.\n\n"
        f"Text:\n{cleaned}\n\n"
        "Clean rewrite:"
    )

    out = llm.invoke(prompt)
    return _extract_text(out)


def summarize_text(text: str) -> str:
    llm = get_llm("qwen2_5")

    prompt = (
        "Compress the following text to at most 2 sentences.\n"
        "Use ONLY words and facts present in the input.\n"
        "Do NOT add new details, examples, names, or assumptions.\n"
        "If something is not explicitly stated, do not include it.\n\n"
        f"Text:\n{text}\n\n"
        "Compressed summary:"
    )

    out = llm.invoke(prompt)
    return _extract_text(out)



def clean_and_summarize(raw_input: str) -> str:
    core = extract_core_content(raw_input)
    pruned = semantic_prune(core)
    normalized = normalize_meaning(pruned)
    return summarize_text(normalized)


__all__ = ["clean_and_summarize"]
