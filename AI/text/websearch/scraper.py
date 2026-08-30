import re
import requests
import trafilatura
import logging
import time
from utils.tracer import trace_event

logger = logging.getLogger(__name__)


def clean_raw_text(raw_text: str) -> str:
    """Removes newlines, tabs, extra spaces, and converts to lowercase."""
    text = re.sub(r"[\n\t\r]+", " ", raw_text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip().lower()


def extract_article_text(url: str, snippet: str) -> str:
    """Instantly scrapes and cleans text using pure Python. No LLM delays."""
    try:
        start_time = time.time()
        trace_event("python_ai_worker", "websearch", "web_scrape_started", details={"url": url})
        r = requests.get(
            url,
            timeout=25,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )

        if r.status_code == 200:
            extracted = trafilatura.extract(r.text, include_comments=False)

            if extracted:
                combined_text = f"{extracted} \n\n[search engine snippet: {snippet}]"
                cleaned = clean_raw_text(combined_text)
                duration = int((time.time() - start_time) * 1000)
                trace_event("python_ai_worker", "websearch", "web_scrape", duration_ms=duration, details={"url": url, "status": "success", "length": len(cleaned), "content": cleaned})
                return cleaned

        duration = int((time.time() - start_time) * 1000)
        trace_event("python_ai_worker", "websearch", "web_scrape", duration_ms=duration, details={"url": url, "status": "failed", "error": f"HTTP {r.status_code}" if 'r' in locals() else "No extraction"})

    except Exception as e:
        duration = int((time.time() - start_time) * 1000) if 'start_time' in locals() else None
        trace_event("python_ai_worker", "websearch", "web_scrape", status="failed", duration_ms=duration, details={"url": url, "error": str(e)})
        logger.error(f"Scraping failed for URL: {url}", exc_info=True)

    clean_snippet = clean_raw_text(snippet)
    return f"scraping blocked or failed. search engine snippet: {clean_snippet}"
