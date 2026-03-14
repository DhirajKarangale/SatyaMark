import os
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper

load_dotenv()

serper_api_keys_env = os.getenv("SERPER_API_KEYS", "")
SERPER_API_KEYS = [t.strip() for t in serper_api_keys_env.split(",") if t.strip()]

if not SERPER_API_KEYS:
    print("[Warning] No Serper API keys found. Please set SERPER_API_KEYS in .env")

_current_serper_key_index = 0

SEARCH_COUNT = 20
MAX_DAYS_OLD = 14

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
                print(
                    f"[Warning] Serper API key index {_current_serper_key_index} failed. Rotating key..."
                )
                _current_serper_key_index = (_current_serper_key_index + 1) % len(
                    SERPER_API_KEYS
                )
                attempts += 1
            else:
                print(f"[Error] Search failed: {e}")
                return {}

    return {}


def extract_urls_with_meta(result: dict) -> list:
    """Extracts ONLY valid, non-social-media URLs along with their snippets."""
    out = []
    for item in result.get("organic", []):
        url = item.get("link")

        if not url or is_excluded(url):
            continue

        out.append(
            {
                "url": url,
                "snippet": item.get("snippet", ""),
            }
        )

    return out


def get_urls_with_meta(query: str) -> list:
    """
    Fetches the most relevant search results strictly within the MAX_DAYS_OLD window.
    """
    results = []
    seen_urls = set()

    time_filter = f"qdr:d{MAX_DAYS_OLD}"
    search_data = serper_search(query, tbs=time_filter)
    valid_urls = extract_urls_with_meta(search_data)

    for item in valid_urls:
        if item["url"] not in seen_urls:
            results.append(item)
            seen_urls.add(item["url"])

    return results
