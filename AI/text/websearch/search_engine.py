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
URLS_COUNT = 10

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
]


def is_excluded(url: str) -> bool:
    """Checks if a URL belongs to a social media or excluded domain."""
    url = url.lower()
    return any(domain in url for domain in EXCLUDED_DOMAINS)


def serper_search(query: str, tbs: str | None = None) -> dict:
    """
    Executes a Google search via Serper API.
    If a key runs out of credits or throws an auth error, it rotates to the next key.
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
                keyword in error_msg
                for keyword in [
                    "unauthorized",
                    "credit",
                    "403",
                    "429",
                    "limit",
                    "forbidden",
                ]
            ):
                print(
                    f"[Warning] Serper API key index {_current_serper_key_index} failed/out of credits. Rotating key..."
                )
                _current_serper_key_index = (_current_serper_key_index + 1) % len(
                    SERPER_API_KEYS
                )
                attempts += 1
            else:
                print(f"[Error] Serper search failed with a standard error: {e}")
                return {}

    print("[Error] All Serper API keys exhausted or failed.")
    return {}


def extract_urls_with_meta(result: dict, freshness: str) -> list:
    """Extracts valid, non-excluded URLs along with their snippets and metadata."""
    out = []
    for item in result.get("organic", []):
        url = item.get("link")
        if not url or is_excluded(url):
            continue

        out.append(
            {
                "url": url,
                "freshness": freshness,
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "date": item.get("date", ""),
            }
        )

        if len(out) == URLS_COUNT:
            break

    return out


def get_urls_with_meta(query: str) -> list:
    """
    Fetches recent and older search results, combines them,
    and returns a clean list of dictionaries containing URLs and snippets.
    """
    results = []

    recent = serper_search(query, tbs="qdr:w")
    results.extend(extract_urls_with_meta(recent, freshness="last_7_days"))

    if len(results) < URLS_COUNT:
        older = serper_search(query)
        older_urls = extract_urls_with_meta(older, freshness="older")

        existing_urls = {r["url"] for r in results}
        for item in older_urls:
            if item["url"] not in existing_urls:
                results.append(item)
            if len(results) == URLS_COUNT:
                break

    return results[:URLS_COUNT]
