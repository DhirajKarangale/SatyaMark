import requests
import trafilatura


def extract_article_text(url: str, snippet: str) -> str:
    """Attempts to scrape the full article. Falls back to the search snippet if blocked."""
    try:
        r = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "AcceptLanguage": "en-US,en;q=0.9",
            },
        )
        if r.status_code == 200:
            extracted = trafilatura.extract(r.text, include_comments=False)
            if extracted and len(extracted.strip()) > 100:
                return extracted.strip()[:4000]
    except Exception as e:
        pass

    return f"Scraping blocked. Search Engine Snippet: {snippet}"
