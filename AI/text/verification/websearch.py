import os
import re
import requests
import trafilatura
from text.utils.huggingface import invoke
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper

load_dotenv()

serper_api_keys_env = os.getenv("SERPER_API_KEYS")
SERPER_API_KEYS = [t.strip() for t in serper_api_keys_env.split(",") if t.strip()]

if not SERPER_API_KEYS:
    raise ValueError("No Serper API keys found. Please set SERPER_API_KEYS in .env")

_current_serper_key_index = 0

QUERY_MODELS = ["deepseek_r1", "deepseek_v3", "qwen2_5", "llama3"]
SEARCH_COUNT = 20
URLS_COUNT = 10

prompt_template = """
You are an expert at converting any claim or statement into a **strong, precise, factual web search query**.

Your output must help the user find **verified information** about what really happened.

Rules:
- If the input is a claim, convert it into a **neutral fact-checking question**.
  Examples:
  - "3 aliens involve in Delhi bomb blast" → "who was actually involved in the Delhi bomb blast"
  - "Aliens attacked London" → "what actually happened in the London attack"
  - "Elon Musk bought Google" → "did Elon Musk buy Google"
  - "There is big car accident in Pune on 10 Nov 2025" → "what happened in the Pune car accident on 10 Nov 2025"
- Remove fictional or impossible details (like aliens) and focus on the **real event**.
- Query can be long if needed — **precision is more important than length**.
- DO NOT include any reasoning, tags, or explanations.  
- Return only the final query string.

Statement:
{text}

Return ONLY the rewritten search query.
"""

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


def get_query(text: str) -> str:
    prompt = prompt_template.format(text=text)
    try:
        raw = invoke(QUERY_MODELS, prompt, parse_as_json=False)
        lines = [line.strip() for line in raw.split("\n") if line.strip()]
        if not lines:
            return text

        final = lines[-1].strip().strip('"').strip("'").strip("`")
        return re.sub(r"\s+", " ", final).strip()
    except Exception:
        return text


def is_excluded(url: str):
    url = url.lower()
    return any(domain in url for domain in EXCLUDED_DOMAINS)


def serper_search(query: str, tbs: str | None = None):
    """
    Executes a Google search via Serper API.
    If a key runs out of credits or throws an auth error, it rotates to the next key.
    """
    global _current_serper_key_index
    attempts = 0

    while attempts < len(SERPER_API_KEYS):
        current_key = SERPER_API_KEYS[_current_serper_key_index]
        try:
            search = GoogleSerperAPIWrapper(
                serper_api_key=current_key,
                search_params={"tbs": tbs} if tbs else None,
            )
            results = search.results(query, n=SEARCH_COUNT)

            # Serper occasionally returns an error dictionary instead of raising an exception natively
            if isinstance(results, dict) and results.get("message") == "Unauthorized.":
                raise ValueError("Unauthorized. Likely out of credits.")

            return results

        except Exception as e:
            error_msg = str(e).lower()
            # Catch common rate-limit or billing errors from Serper
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
                return (
                    {}
                )  # Return empty dict so the scraper just safely skips web search

    print("[Error] All Serper API keys exhausted or failed.")
    return {}


def extract_urls(result):
    urls = []
    for item in result.get("organic", []):
        url = item.get("link")
        if not url or is_excluded(url):
            continue
        urls.append(url)
        if len(urls) == URLS_COUNT:
            break
    return urls


def extract_urls_with_meta(result, freshness):
    out = []
    for item in result.get("organic", []):
        url = item.get("link")
        if not url or is_excluded(url):
            continue
        out.append(
            {
                "url": url,
                "freshness": freshness,
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "date": item.get("date"),
            }
        )
        if len(out) == URLS_COUNT:
            break
    return out


def get_urls_with_meta(query: str):
    results = []

    recent = serper_search(query, tbs="qdr:w")
    results.extend(extract_urls_with_meta(recent, freshness="last_7_days"))

    if len(results) < URLS_COUNT:
        older = serper_search(query)
        older_urls = extract_urls_with_meta(older, freshness="older")

        existing = {r["url"] for r in results}
        for item in older_urls:
            if item["url"] not in existing:
                results.append(item)
            if len(results) == URLS_COUNT:
                break

    return results[:URLS_COUNT]


def extract_text(url_items):
    results = []

    for item in url_items:
        url = item["url"]
        try:
            r = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"},
            )

            text = ""
            if r.status_code == 200:
                extracted = trafilatura.extract(
                    r.text,
                    include_comments=False,
                )
                text = extracted.strip() if extracted else ""

            results.append(
                {
                    **item,
                    "data": text,
                }
            )

        except Exception:
            results.append(
                {
                    **item,
                    "data": "",
                }
            )

    return results


def get_content(statement: str):
    query = get_query(statement)
    urls = get_urls_with_meta(query)
    content = extract_text(urls)
    return content
