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

    if re.fullmatch(r"([@#][a-zA-Z0-9_]+\s*)+", s):
        return True

    # Matches usernames without @ or tags without # (e.g., tech_insider, john_doe123)
    if re.fullmatch(r"[a-zA-Z0-9_]+", s) and len(s) <= 25:
        return True

    # We removed date filtering here so that important dates get passed to the summarizer.

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
        cleaned = ". ".join(meaningful_parts)

    cleaned = cleaned.replace("\u00a0", " ")

    final = re.sub(r"\s+", " ", cleaned).lower().strip()
    return final
