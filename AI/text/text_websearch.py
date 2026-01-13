import os
import re
import requests
import trafilatura
from connect import get_llm
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities import GoogleSerperAPIWrapper

load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
llm = get_llm("deepseek_r1")

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

prompt = ChatPromptTemplate.from_template(prompt_template)
output_parser = StrOutputParser()

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


def get_query(text: str):
    response = (prompt | llm | output_parser).invoke({"text": text})

    raw = str(response)
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL | re.IGNORECASE)
    raw = re.sub(r"</?think>", "", raw, flags=re.IGNORECASE)

    lines = [line.strip() for line in raw.split("\n") if line.strip()]
    if not lines:
        return ""

    final = lines[-1]
    final = final.strip().strip('"').strip("'").strip("`")
    final = re.sub(r"\s+", " ", final).strip()

    return final


def is_excluded(url: str):
    url = url.lower()
    return any(domain in url for domain in EXCLUDED_DOMAINS)


def serper_search(query: str, tbs: str | None = None):
    search = GoogleSerperAPIWrapper(
        serper_api_key=SERPER_API_KEY,
        search_params={"tbs": tbs} if tbs else None,
    )
    return search.results(query, n=SEARCH_COUNT)


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
