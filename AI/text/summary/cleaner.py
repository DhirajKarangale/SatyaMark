import re
from html import unescape
from typing import List

SEPARATOR = "|#|"


def remove_social_artifacts(text: str) -> str:
    """Removes URLs, UI bait, and engagement metrics from text."""
    text = re.sub(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        "",
        text,
    )

    text = re.sub(
        r"(?i)\b\d+(?:\.\d+)?[KkMmBb]?\s*(?:likes|retweets|reposts|quotes|views|bookmarks|comments)\b",
        "",
        text,
    )

    text = re.sub(
        r"(?i)\b(?:likes|retweets|reposts|quotes|views|bookmarks|comments)\s*:?\s*\d+(?:\.\d+)?[KkMmBb]?\b",
        "",
        text,
    )

    text = re.sub(
        r"(?i)\b(?:show|read|click|view|share)\s+(?:more|full|here|link|thread)\b",
        "",
        text,
    )
    text = re.sub(r"^[•·▪\-\s]*RT\s*:?\s*", "", text)

    return text


def is_social_metadata(segment: str) -> bool:
    """Strictly identifies if an ENTIRE segment is pure metadata."""
    s = segment.strip()
    if not s:
        return True

    if re.fullmatch(r"(@[a-zA-Z0-9_]+\s*)+", s):
        return True

    date_time_patterns = [
        r"(?i)\d+\s*[hmdswy]",
        r"(?i)\d+\s+(?:sec|min|hr|day|week|month|year)s?(?:\s+ago)?",
        r"(?i)(?:just now|today|yesterday|tomorrow)",
        r"\d{1,4}[-/\.\s]+\d{1,2}[-/\.\s]+\d{1,4}",
        r"(?i)\d{1,2}(?:st|nd|rd|th)?[-/\.\s,]+[a-z]{3,10}(?:[-/\.\s,]+\d{2,4})?",
        r"(?i)[a-z]{3,10}[-/\.\s,]+\d{1,2}(?:st|nd|rd|th)?(?:[-/\.\s,]+\d{2,4})?",
        r"(?i)\d{4}[-/\.\s,]+[a-z]{3,10}[-/\.\s,]+\d{1,2}(?:st|nd|rd|th)?",
        r"(?i)\d{1,2}:\d{2}(?::\d{2})?(?:\s*[ap]\.?m\.?)?",
        r"(?i)\d{1,2}\s*[ap]\.?m\.?",
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?",
    ]

    if any(re.fullmatch(pattern, s) for pattern in date_time_patterns):
        return True

    if re.fullmatch(r"\d+(?:,\d{3})*(?:\.\d+)?[KkMmBb]?", s):
        return True

    return False


def clean_raw_social_text(raw_text: str) -> str:
    """Main pipeline execution to scrub raw text before LLM processing."""
    if not raw_text:
        return ""

    cleaned = unescape(raw_text)

    cleaned = remove_social_artifacts(cleaned)

    cleaned = re.sub(r"<[^>]+>", " ", cleaned)

    cleaned = re.sub(r"\s*\|\#\|\s*", SEPARATOR, cleaned)

    if SEPARATOR in cleaned:
        parts: List[str] = [p.strip() for p in cleaned.split(SEPARATOR) if p.strip()]

        meaningful_parts = [p for p in parts if not is_social_metadata(p)]
        cleaned = f" {SEPARATOR} ".join(meaningful_parts)

    cleaned = cleaned.replace("\u00a0", " ")

    final = re.sub(r"\s+", " ", cleaned).lower().strip()
    return final
