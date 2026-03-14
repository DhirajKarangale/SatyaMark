import concurrent.futures
from websearch.query_builder import generate_search_query
from websearch.search_engine import get_urls_with_meta
from websearch.scraper import extract_article_text
from websearch.verifier import fact_check

MAX_WORKERS = 5
MAX_URLS_TO_VERIFY = 10


def web_verify(claim: str):
    query = generate_search_query(claim)
    search_results = get_urls_with_meta(query)

    if not search_results:
        print("[Warning] No search results found. Returning insufficient.")
        return fact_check(claim, [])

    scraped_dict = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_item = {
            executor.submit(extract_article_text, item["url"], item["snippet"]): item
            for item in search_results
        }

        for future in concurrent.futures.as_completed(future_to_item):
            item = future_to_item[future]
            try:
                text = future.result()
                scraped_dict[item["url"]] = text
            except Exception as e:
                print(f"[Error] Failed to process {item['url']}: {e}")

    ordered_scraped_data = []
    for item in search_results:
        url = item["url"]
        if url in scraped_dict and len(scraped_dict[url]) > 50:
            ordered_scraped_data.append({"url": url, "data": scraped_dict[url]})

    final_evidence = ordered_scraped_data[:MAX_URLS_TO_VERIFY]

    result = fact_check(claim, final_evidence)
    return result
