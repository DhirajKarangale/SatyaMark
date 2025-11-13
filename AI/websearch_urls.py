from langchain_community.utilities import GoogleSerperAPIWrapper
from dotenv import load_dotenv
import os

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
