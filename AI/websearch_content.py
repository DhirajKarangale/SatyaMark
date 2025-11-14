import os
import time
import json, re
import requests
import trafilatura
from connect import get_llm
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities import GoogleSerperAPIWrapper

load_dotenv()
SERPER = os.getenv("SERPER")
llm = get_llm("mistral")  # mistral, llama3, deepseek_r1

URLS_COUNT = 2

prompt_template = """
You will receive raw text scraped from a webpage. The text may include noise such as HTML, footers, navigation menus, CSS, scripts, timestamps, embedded references, metadata, disclaimers, or repeated lines.

Your task: 
Extract a clean, compact factual summary that contains EVERY important data point from the meaningful content.

STRICT RULES:
- Do NOT output reasoning or chain-of-thought.
- Do NOT output examples or explanations.
- Do NOT mention missing text or the fact that content was scraped.
- Do NOT add fabricated or hypothetical information.
- Do NOT restate these instructions.
- Do NOT include HTML, tags, UI text, or irrelevant boilerplate.
- Do NOT produce long sentences.

WHAT TO REMOVE:
- HTML tags, CSS, JS
- Navigation menus, footers, cookie notices, ads
- Duplicated lines
- Broken/incomplete fragments
- Irrelevant or unrelated text
- Citation numbers like [1], [2], etc.

WHAT TO KEEP:
- All events, entities, dates, locations, numbers, casualties
- All verifiable, factual information
- All investigative details
- All reactions & statements
- All timeline-relevant timestamps
- All statistics and measurements

OUTPUT FORMAT:
A short, compressed factual summary in clear sentences suitable for another AI agent.
No bullets. No lists. No formatting. Just clean summary text.

RAW INPUT:
{{input_text}}

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


def is_excluded(url: str):
    url = url.lower()
    return any(domain in url for domain in EXCLUDED_DOMAINS)


def get_urls(query: str):
    search = GoogleSerperAPIWrapper(SERPER=SERPER)
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


def chunk_text(text, max_chars=1500):
    text = re.sub(r"\s+", " ", text).strip()

    sentences = re.split(r"(?<=[.!?]) +", text)

    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) <= max_chars:
            current += " " + sentence
        else:
            chunks.append(current.strip())
            current = sentence

    if current:
        chunks.append(current.strip())

    return chunks


def safe_invoke(chain, payload, retries=2):
    for i in range(retries):
        try:
            return chain.invoke(payload)
        except Exception as e:
            print(f"Retry {i+1} failed:", e)
            time.sleep(0.5)
    return None


def clean_content(content):
    cleaned_results = []
    chain = prompt | llm | output_parser

    for item in content:
        url = item.get("url")
        raw = item.get("data", "").strip()

        if not raw:
            continue

        chunks = chunk_text(raw, max_chars=1500)

        summaries = []

        for chunk in chunks:
            output = safe_invoke(chain, {"input_text": chunk})
            if not output:
                print(f"Skipping failed chunk for: {url}")
                continue

            clean_out = re.sub(r"\s+", " ", output).strip()
            summaries.append(clean_out)

        final_summary = " ".join(summaries)
        final_summary = re.sub(r"\s+", " ", final_summary).strip()

        cleaned_results.append({"url": url, "data": final_summary})

    return cleaned_results


def get_content(query: str):
    urls = get_urls(query)
    content = extract_text(urls)
    print("\nConent: ", content)
    clean = clean_content(content)
    # print("\nCleaned: ", clean)

    return clean
