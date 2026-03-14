import re
import requests
import trafilatura
from text.utils.huggingface import invoke

CLEANUP_MODELS = ["qwen2_5", "deepseek_v3", "deepseek_r1"]

cleanup_prompt = """
You are a strict data processing assistant. I am providing you with raw scraped web text, with a search engine snippet appended at the very end for extra context.
Your task is to extract the core story and remove all remaining noise.

Rules:
1. Retain 100% of the factual information, claims, names, dates, numbers, and core reporting.
2. INTEGRATE the information from the appended Search Snippet. Do not discard it, as it contains the specific keywords that matched the user's query.
3. Remove all advertisements, newsletter signups, cookie notices, and irrelevant boilerplate.
4. Remove all leftover HTML tags (e.g., <div>, <p>, <span>), special formatting characters (like \\n, \\t, \\r, *, #), and markdown artifacts.
5. DO NOT hallucinate or add any new information.
6. Return the output as a clean, continuous block of plain text.

Text to clean:
{text}

Return ONLY the cleaned text. No conversational filler.
"""


def clean_raw_text(raw_text: str) -> str:
    """Removes newlines, tabs, extra spaces, and converts to lowercase."""
    text = re.sub(r"[\n\t\r]+", " ", raw_text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip().lower()


def extract_article_text(url: str, snippet: str) -> str:
    try:
        r = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )

        if r.status_code == 200:
            extracted = trafilatura.extract(r.text, include_comments=False)

            if extracted and len(extracted.strip()) > 100:
                combined_text = f"{extracted} \n\n[Additional Context from Search Snippet: {snippet}]"

                cleaned_base = clean_raw_text(combined_text)

                try:
                    prompt = cleanup_prompt.format(text=cleaned_base)
                    llm_cleaned = invoke(CLEANUP_MODELS, prompt, parse_as_json=False)

                    if llm_cleaned and len(llm_cleaned.strip()) > 50:
                        return llm_cleaned.strip().lower()

                    return cleaned_base
                except Exception as e:
                    print(
                        f"[Warning] LLM cleanup failed for {url}, using regex cleaned text."
                    )
                    return cleaned_base

    except Exception as e:
        pass

    clean_snippet = clean_raw_text(snippet)
    return f"scraping blocked. search engine snippet: {clean_snippet}"
