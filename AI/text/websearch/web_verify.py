import concurrent.futures
from text.websearch.query_builder import generate_search_query
from text.websearch.search_engine import get_urls_with_meta
from text.websearch.scraper import extract_article_text
from text.websearch.verifier import fact_check

MAX_WORKERS = 3


def web_verify(claim: str):
    query = generate_search_query(claim)
    search_results = get_urls_with_meta(query)

    scraped_data = []

    if not search_results:
        print("[Warning] No search results found. Returning insufficient.")
        return fact_check(claim, [])
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        future_to_item = {
            executor.submit(extract_article_text, item["url"], item["snippet"]): item
            for item in search_results
        }

        for future in concurrent.futures.as_completed(future_to_item):
            item = future_to_item[future]
            try:
                text = future.result()
                scraped_data.append({"url": item["url"], "data": text})
            except Exception as e:
                print(f"Failed to process {item['url']}: {e}")

    result = fact_check(claim, scraped_data)
    return result


state = "India has LPG gas shortage"
print("\n\n", web_verify(state))
