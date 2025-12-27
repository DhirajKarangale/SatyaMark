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

URLS_COUNT = 5

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


def get_urls(query: str):
    search = GoogleSerperAPIWrapper(SERPER=SERPER_API_KEY)
    result = search.results(query, n=20)

    organic_results = result.get("organic", [])

    urls = []

    for item in organic_results:
        url = item.get("link")
        if not url:
            continue

        if is_excluded(url):
            continue

        urls.append(url)

        if len(urls) == URLS_COUNT:
            break

    return urls


def extract_text(urls):
    results = []

    for url in urls:
        try:
            r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})

            if r.status_code != 200:
                results.append({"url": url, "data": ""})
                continue

            downloaded = trafilatura.extract(r.text, include_comments=False)
            clean_text = downloaded if downloaded else ""
            results.append({"url": url, "data": clean_text.strip()})

        except Exception:
            results.append({"url": url, "data": ""})

    return results


def get_content(statement: str):
    query = get_query(statement)
    urls = get_urls(query)
    content = extract_text(urls)

    return content
