# text_summarize.py
from typing import Any, List, Tuple
import re
from html import unescape
# Optional: pip install langdetect
try:
    from langdetect import detect  # type: ignore
except Exception:
    detect = None

from connect import get_llm

# Small stopword list for content-word checking (keeps function self-contained)
_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "these", "those", "a", "an",
    "in", "on", "at", "to", "of", "is", "are", "was", "were", "be", "been",
    "by", "as", "it", "its", "from", "or", "but", "not", "which", "will",
    "can", "may", "has", "have", "had"
}


def _extract_text(output: Any) -> str:
    """Normalize LLM outputs (AIMessage, dict, or str) into a clean string."""
    if hasattr(output, "content"):
        return (output.content or "").strip()
    if isinstance(output, dict) and "content" in output:
        return (output.get("content") or "").strip()
    return (str(output) if output is not None else "").strip()


def _looks_english(text: str) -> bool:
    """Detect English language or fallback to heuristic."""
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


def _split_sentences(text: str) -> List[str]:
    """Very small sentence splitter: split on .!? followed by whitespace (keeps punctuation)."""
    sents = re.split(r'(?<=[\.\!\?])\s+', text.strip())
    return [s.strip() for s in sents if s.strip()]


def _normalize_token(token: str) -> str:
    """Lowercase and strip punctuation for token comparison."""
    return re.sub(r'[^\w]', '', token.lower())


def _content_tokens(text: str) -> List[str]:
    """
    Return tokens considered 'content' (length>2 and not in stopwords), normalized.
    This helps compare whether the summary uses words seen in the input.
    """
    tokens = re.findall(r"\w+", text.lower())
    content = [t for t in tokens if len(t) > 2 and t not in _STOPWORDS]
    return [t for t in content]


def _is_extractive(summary: str, source: str, min_fraction: float = 0.7) -> bool:
    """
    Check if summary is 'mostly' extractive from source:
      - Compute fraction of content tokens in summary that appear in the source.
      - If >= min_fraction -> consider safe (not inventing).
    """
    s_tokens = _content_tokens(summary)
    if not s_tokens:
        return True  # nothing to check (empty), treat as safe
    src_tokens_set = set(_content_tokens(source))
    match_count = sum(1 for t in s_tokens if t in src_tokens_set)
    frac = match_count / len(s_tokens)
    return frac >= min_fraction


def _extractive_fallback(source: str, max_sentences: int = 2) -> str:
    """
    Simple extractive fallback: pick up to `max_sentences` sentences from source that
    maximize content-token coverage. Does not invent new facts.
    """
    sentences = _split_sentences(source)
    if not sentences:
        return ""

    src_tokens = set(_content_tokens(source))
    # Score sentences by count of content tokens present (higher = better)
    scored: List[Tuple[int, int, str]] = []
    for idx, s in enumerate(sentences):
        tokens = _content_tokens(s)
        score = sum(1 for t in tokens if t in src_tokens)
        scored.append((score, -idx, s))  # use -idx to prefer earlier on tie-break

    # pick top max_sentences by score
    scored.sort(reverse=True)
    chosen = [tup[2] for tup in scored[:max_sentences]]
    # preserve original order as much as possible: sort by original index within source
    chosen_sorted = sorted(chosen, key=lambda s: sentences.index(s))
    return " ".join(chosen_sorted).strip()


def _extract_overall_section(raw: str) -> str:
    """
    Extract explicit 'Overall'/'Summary' section if present; else use last paragraph.
    """
    if not raw:
        return ""
    # Try explicit labels
    match = re.search(r'(?im)^(?:\s*(Overall|Summary|Gist|Conclusion)\s*[:\-–—]\s*)(.+)$', raw, re.MULTILINE | re.DOTALL)
    if match:
        content = match.group(2).strip()
        # collapse whitespace/newlines
        content = re.sub(r'\s+', ' ', content).strip()
        return content
    # Otherwise fallback to last paragraph
    parts = [p.strip() for p in re.split(r'\n\s*\n', raw) if p.strip()]
    if parts:
        return re.sub(r'\s+', ' ', parts[-1]).strip()
    # finally, whole text
    return re.sub(r'\s+', ' ', raw).strip()

def _clean_input_text(text: str) -> str:
    """
    Clean HTML tags, metadata, and social media markup (hashtags, mentions, links).
    Keeps only readable, factual content.
    """
    if not text:
        return ""

    # 1. Unescape HTML entities (&amp;, &lt;, etc.)
    text = unescape(text)

    # 2. Remove HTML tags (<p>, <br>, <strong>, <a>, etc.)
    text = re.sub(r"<[^>]+>", " ", text)

    # 3. Remove URLs
    text = re.sub(r"http\S+", " ", text)

    # 4. Remove hashtags and mentions (Twitter-like)
    text = re.sub(r"[@#]\w+", " ", text)

    # 5. Collapse extra whitespace and emojis (optional — emojis are fine if you want to keep them)
    text = re.sub(r"\s+", " ", text).strip()

    return text

def summarize_text(text: str, *, enforce_english: bool = True) -> str:
    """
    Summarize input text into a short, simple English gist (2 sentences max),
    while ensuring no new facts are introduced.

    Strategy:
      1. Ask LLM for a concise 2-sentence summary with explicit instruction
         not to add facts and to prefer phrases from the input.
      2. Extract the model's 'overall' paragraph.
      3. Verify the model output is largely extractive (content-token overlap).
         If it looks like the model added new facts, fall back to a purely extractive
         method that selects up to two sentences from the original input.
    """
    llm = get_llm("llama3")

    system_msg = (
        "You are a professional summarizer. Produce a very short gist in plain English.\n"
        "IMPORTANT: Do NOT add any new facts or information that is not present in the input.\n"
        "Prefer exact phrases from the input when possible. Output only the final summary paragraph\n"
        "— no bullets, no labels, no headings. Keep the summary extremely short (up to 2 sentences)."
    )

    fewshot_user = (
        "Résumé (français): « Le rapport explique la baisse des ventes au T2 et propose trois actions pour le T3. »"
    )
    fewshot_assistant = (
        "The report explains why Q2 sales dropped and outlines three actions planned to boost Q3 performance."
    )
    clean_text = _clean_input_text(text)
    human_msg = f"Text to summarize:\n{clean_text}"

    prompt = "\n\n".join([
        f"SYSTEM:\n{system_msg}",
        f"User:\n{fewshot_user}",
        f"Assistant:\n{fewshot_assistant}",
        f"User:\n{human_msg}",
        "Assistant:"
    ])

    # First pass
    raw = llm.invoke(prompt)
    raw_text = _extract_text(raw)
    # Try to get the 'overall' gist piece (in case model included other sections)
    overall = _extract_overall_section(raw_text)

    # Optionally enforce English
    if enforce_english and not _looks_english(overall):
        force_prompt = (
            "Rewrite the following in plain, simple English only. Output up to 2 sentences and nothing else.\n\n"
            f"Draft:\n{overall or raw_text}"
        )
        forced = llm.invoke(force_prompt)
        overall = _extract_text(forced)
        overall = _extract_overall_section(overall)

    # Verification: ensure summary is mostly extractive from source
    if overall and _is_extractive(overall, text, min_fraction=0.7):
        # Good: return the overall summary (trim to 2 sentences max)
        sents = _split_sentences(overall)
        if not sents:
            return overall.strip()
        # return up to 2 sentences, preserving punctuation
        return " ".join(sents[:2]).strip()
    else:
        # Fallback: purely extractive selection from the input (guarantees no new facts)
        fallback = _extractive_fallback(text, max_sentences=2)
        # If fallback is empty, as a safe last resort, return the raw overall (even if non-extractive)
        return fallback if fallback else ((" ".join(_split_sentences(overall)[:2])) if overall else "").strip()


__all__ = ["summarize_text"]
