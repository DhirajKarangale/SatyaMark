from langchain_community.utilities import GoogleSerperAPIWrapper
from dotenv import load_dotenv
import os
import requests
import trafilatura

load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

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
    search = GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)
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

        if len(urls) == 10:
            break

    return urls


def extract_clean_text(urls):
    results = []

    for url in urls:
        try:
            r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})

            if r.status_code != 200:
                results.append({"url": url, "data": ""})
                continue

            downloaded = trafilatura.extract(r.text, include_comments=False)

            # If extraction fails, return empty string for that URL
            clean_text = downloaded if downloaded else ""

            results.append({"url": url, "data": clean_text.strip()})

        except Exception:
            results.append({"url": url, "data": ""})

    return results


def test(text):
    # dk = get_urls(text)
    dk = [
        "https://www.reuters.com/world/india/what-do-we-know-about-delhi-car-blast-that-killed-eight-people-2025-11-11/",
        "https://www.nytimes.com/2025/11/11/world/asia/india-delhi-explosion-terror.html",
        "https://www.ndtv.com/india-news/red-fort-blast-delhi-blast-delhi-vs-meerut-red-fort-blast-victims-family-fight-over-place-of-burial-9619250"
    ]
    clean = extract_clean_text(dk)
    # print("URLS: ", dk)
    print("Clean: ", clean)
