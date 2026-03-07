import re
from html import unescape
from typing import List

SEPARATOR = "|#|"


def remove_social_artifacts(text: str) -> str:
    """Removes URLs, UI bait, and engagement metrics from text."""
    # 1. Remove URLs
    text = re.sub(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        "",
        text,
    )

    # 2. Catch standard & squished metrics (e.g., "132 Likes", "132likes")
    text = re.sub(
        r"(?i)\b\d+(?:\.\d+)?[KkMmBb]?\s*(?:likes|retweets|reposts|quotes|views|bookmarks|comments)\b",
        "",
        text,
    )

    # 3. Catch reversed metrics (e.g., "comments 23", "Likes: 1.2K")
    text = re.sub(
        r"(?i)\b(?:likes|retweets|reposts|quotes|views|bookmarks|comments)\s*:?\s*\d+(?:\.\d+)?[KkMmBb]?\b",
        "",
        text,
    )

    # 4. Catch UI bait and standard social prefixes
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

    # 1. Handles (Catches single or multiple: "@user1 @user2")
    if re.fullmatch(r"(@[a-zA-Z0-9_]+\s*)+", s):
        return True

    # 2. Comprehensive Date & Time Patterns
    date_time_patterns = [
        # Relative time (short): 5h, 12m, 2d, 3w, 1y
        r"(?i)\d+\s*[hmdswy]",
        # Relative time (worded): 5 days ago, 10 mins, just now, today, yesterday
        r"(?i)\d+\s+(?:sec|min|hr|day|week|month|year)s?(?:\s+ago)?",
        r"(?i)(?:just now|today|yesterday|tomorrow)",
        # Universal Numeric Dates: DD-MM-YYYY, YYYY.MM.DD, MM/DD/YY, etc.
        r"\d{1,4}[-/\.\s]+\d{1,2}[-/\.\s]+\d{1,4}",
        # Day-First Word Dates: 22-August-2026, 22nd Aug, 2026, 22 Aug
        r"(?i)\d{1,2}(?:st|nd|rd|th)?[-/\.\s,]+[a-z]{3,10}(?:[-/\.\s,]+\d{2,4})?",
        # Month-First Word Dates: August-22-2025, Aug 22 2025, August 22nd, 2025
        r"(?i)[a-z]{3,10}[-/\.\s,]+\d{1,2}(?:st|nd|rd|th)?(?:[-/\.\s,]+\d{2,4})?",
        # Year-First Word Dates: 2025 August 22, 2025-Aug-22
        r"(?i)\d{4}[-/\.\s,]+[a-z]{3,10}[-/\.\s,]+\d{1,2}(?:st|nd|rd|th)?",
        # Standard Times: 12:30, 1:45 PM, 14:00:59, 5 am, 5a.m.
        r"(?i)\d{1,2}:\d{2}(?::\d{2})?(?:\s*[ap]\.?m\.?)?",
        r"(?i)\d{1,2}\s*[ap]\.?m\.?",
        # ISO 8601 / API Timestamps: 2023-10-12T15:30:00Z, 2025-08-17T00:00:00+00:00
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?",
    ]

    if any(re.fullmatch(pattern, s) for pattern in date_time_patterns):
        return True

    # 3. Pure Numbers / Standalone view counts ("1,234" or "1.5K")
    if re.fullmatch(r"\d+(?:,\d{3})*(?:\.\d+)?[KkMmBb]?", s):
        return True

    return False


def clean_raw_social_text(raw_text: str) -> str:
    """Main pipeline execution to scrub raw text before LLM processing."""
    if not raw_text:
        return ""

    # Decode HTML entities (&amp; to &)
    cleaned = unescape(raw_text)

    # Strip engagement bait and URLs
    cleaned = remove_social_artifacts(cleaned)

    # Remove raw HTML tags
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)

    # Standardize separator spacing
    cleaned = re.sub(r"\s*\|\#\|\s*", SEPARATOR, cleaned)

    # Process individual segments
    if SEPARATOR in cleaned:
        parts: List[str] = [p.strip() for p in cleaned.split(SEPARATOR) if p.strip()]

        # Keep only segments that are NOT pure metadata
        meaningful_parts = [p for p in parts if not is_social_metadata(p)]
        cleaned = f" {SEPARATOR} ".join(meaningful_parts)

    # Final whitespace cleanup
    cleaned = cleaned.replace("\u00a0", " ")

    final = re.sub(r"\s+", " ", cleaned).lower().strip()
    return final
