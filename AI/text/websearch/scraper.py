import re
import requests
import trafilatura


def clean_raw_text(raw_text: str) -> str:
    """Removes newlines, tabs, extra spaces, and converts to lowercase."""
    text = re.sub(r"[\n\t\r]+", " ", raw_text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip().lower()


def extract_article_text(url: str, snippet: str) -> str:
    """Instantly scrapes and cleans text using pure Python. No LLM delays."""
    try:
        r = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )

        if r.status_code == 200:
            extracted = trafilatura.extract(r.text, include_comments=False)

            if extracted:
                combined_text = f"{extracted} \n\n[search engine snippet: {snippet}]"
                return clean_raw_text(combined_text)

    except Exception:
        pass

    clean_snippet = clean_raw_text(snippet)
    return f"scraping blocked or failed. search engine snippet: {clean_snippet}"
