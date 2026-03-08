from text.websearch.query_builder import generate_search_query
from text.websearch.search_engine import get_urls_with_meta
from text.websearch.scraper import extract_article_text
from text.websearch.verifier import fact_check


def verify_claim(claim: str):
    query = generate_search_query(claim)
    search_results = get_urls_with_meta(query)
    scraped_data = []
    for item in search_results:
        text = extract_article_text(item["url"], item["snippet"])
        scraped_data.append({"url": item["url"], "data": text})

    result = fact_check(claim, scraped_data)
    return result


# Example usage:
# print(verify_claim("Aliens attacked London yesterday"))
print(
    verify_claim("USA started war with iran, they did bombing on some of iran places")
)
