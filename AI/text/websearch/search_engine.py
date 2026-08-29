import os
import time
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
import logging

logger = logging.getLogger(__name__)

load_dotenv()

serper_api_keys_env = os.getenv("SERPER_API_KEYS", "")
SERPER_API_KEYS = [t.strip() for t in serper_api_keys_env.split(",") if t.strip()]

if not SERPER_API_KEYS:
    logger.warning("No Serper API keys found. Please set SERPER_API_KEYS in .env")

_current_serper_key_index = 0

SEARCH_COUNT = 20

EXCLUDED_DOMAINS = [
    "youtube.com",
    "youtu.be",
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "tiktok.com",
    "reddit.com",
    "vimeo.com",
    "pinterest.com",
    "linkedin.com",
    "medium.com",
    "quora.com",
    "tumblr.com",
]

CREDIBILITY_TIERS = {
    "tier1": [
        "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "nature.com",
        ".gov", "who.int", "un.org", "nih.gov", "cdc.gov", "nasa.gov",
        "sciencedirect.com", "pubmed.ncbi.nlm.nih.gov",
    ],
    "tier2": [
        "nytimes.com", "washingtonpost.com", "theguardian.com", "wsj.com",
        "economist.com", "scientificamerican.com", "theatlantic.com",
        "npr.org", "pbs.org", "arstechnica.com", "wired.com",
    ],
    "tier3": [
        "wikipedia.org", "snopes.com", "politifact.com", "factcheck.org",
        "fullfact.org", "britannica.com",
    ],
}

CREDIBILITY_WEIGHTS = {"tier1": 1.5, "tier2": 1.3, "tier3": 1.2}


def get_credibility_weight(url: str) -> float:
    """Returns a credibility weight for a URL based on its domain tier."""
    url_lower = url.lower()
    for tier, domains in CREDIBILITY_TIERS.items():
        if any(d in url_lower for d in domains):
            return CREDIBILITY_WEIGHTS[tier]
    return 1.0


def is_excluded(url: str) -> bool:
    """Checks if a URL belongs to a social media or user-generated domain."""
    url = url.lower()
    return any(domain in url for domain in EXCLUDED_DOMAINS)


def serper_search(query: str, tbs: str | None = None) -> dict:
    """
    Executes a Google search via Serper API.
    Handles key rotation automatically if a key runs out of credits or throws an error.
    """
    global _current_serper_key_index
    attempts = 0

    if not SERPER_API_KEYS:
        return {}

    while attempts < len(SERPER_API_KEYS):
        current_key = SERPER_API_KEYS[_current_serper_key_index]
        network_retries = 0
        
        while network_retries < 3:
            try:
                search = GoogleSerperAPIWrapper(
                    serper_api_key=current_key,
                    search_params={"tbs": tbs} if tbs else None,
                )
                results = search.results(query, n=SEARCH_COUNT)

                if isinstance(results, dict) and results.get("message") == "Unauthorized.":
                    raise ValueError("Unauthorized. Likely out of credits.")

                return results

            except Exception as e:
                error_msg = str(e).lower()
                if any(
                    k in error_msg
                    for k in ["unauthorized", "credit", "403", "429", "limit", "forbidden"]
                ):
                    logger.warning(
                        f"Serper API key index {_current_serper_key_index} failed. Rotating key..."
                    )
                    _current_serper_key_index = (_current_serper_key_index + 1) % len(
                        SERPER_API_KEYS
                    )
                    attempts += 1
                    break
                else:
                    network_retries += 1
                    if network_retries < 3:
                        delay = 2 ** network_retries
                        logger.warning(f"Serper search network error: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"Serper search failed after 3 network retries: {e}", exc_info=True)
                        attempts = len(SERPER_API_KEYS)
                        break

    return {}


def extract_urls_with_meta(result: dict) -> list:
    """Extracts ONLY valid, non-social-media URLs along with their snippets and credibility weights."""
    out = []
    for item in result.get("organic", []):
        url = item.get("link")

        if not url or is_excluded(url):
            continue

        out.append(
            {
                "url": url,
                "snippet": item.get("snippet", ""),
                "credibility_weight": get_credibility_weight(url),
            }
        )

    return out


def get_urls_with_meta(query: str) -> list:
    """
    Fetches the most relevant search results.
    """
    results = []
    seen_urls = set()

    search_data = serper_search(query)
    valid_urls = extract_urls_with_meta(search_data)

    for item in valid_urls:
        if item["url"] not in seen_urls:
            results.append(item)
            seen_urls.add(item["url"])

    return results
