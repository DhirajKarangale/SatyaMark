import os
from dotenv import load_dotenv

# ---- Search (free, no API key) ----
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

# ---- Loaders / parsing ----
from langchain_community.document_loaders import WebBaseLoader, PlaywrightURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup
from readability import Document as ReadabilityDoc

# ---- Your HF summarizer chain (reuse your code) ----
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

load_dotenv()

# ---------- LLM chain (same logic as your script) ----------
def build_llama3_summarizer_chain(
    repo_id: str = os.getenv("HF_REPO_ID", "meta-llama/Meta-Llama-3-8B-Instruct"),
    provider: str = os.getenv("HF_PROVIDER", "auto"),
    task: str = os.getenv("HF_TASK", "conversational"),
    max_new_tokens: int = int(os.getenv("MAX_NEW_TOKENS", "512")),
    temperature: float = float(os.getenv("TEMPERATURE", "0.2")),
    repetition_penalty: float = float(os.getenv("REPETITION_PENALTY", "1.03")),
):
    llm = HuggingFaceEndpoint(
        repo_id=repo_id,
        task=task,
        provider=provider,
        max_new_tokens=max_new_tokens,
        do_sample=temperature > 0,
        temperature=temperature,
        repetition_penalty=repetition_penalty,
        return_full_text=False,
    )
    chat = ChatHuggingFace(llm=llm)

    system_msg = (
        "You are a professional summarizer.\n"
        "- ALWAYS respond in ENGLISH ONLY.\n"
        "- Keep key facts, names, numbers, dates.\n"
        "OUTPUT:\n"
        "1) 4–7 bullet points\n"
        "2) 2–3 sentence gist paragraph"
    )

    prompt = ChatPromptTemplate.from_messages(
        [("system", system_msg), ("human", "{text}")]
    )
    return prompt | chat | StrOutputParser()

# ---------- Helpers ----------
def search_links(query: str, k: int = 5):
    search = DuckDuckGoSearchAPIWrapper()
    results = search.results(query, max_results=k)
    return [r["link"] for r in results if "link" in r]

def extract_readable_text(html: str) -> str:
    # Try readability first, then fallback to BS4 get_text
    try:
        doc = ReadabilityDoc(html)
        content_html = doc.summary()
        text = BeautifulSoup(content_html, "html.parser").get_text("\n")
        if text and len(text.split()) > 50:
            return text
    except Exception:
        pass
    # fallback
    return BeautifulSoup(html, "html.parser").get_text("\n", strip=True)

def load_pages(urls, use_js=False, timeout=20000):
    if not urls:
        return []
    if use_js:
        loader = PlaywrightURLLoader(
                urls=urls,
                remove_selectors=["nav", "header", "footer"]
            )

    else:
        loader = WebBaseLoader(urls)
    docs = loader.load()
    # Clean each doc with readability/bs4
    cleaned = []
    for d in docs:
        text = extract_readable_text(d.page_content)
        if text:
            d.page_content = text
            cleaned.append(d)
    return cleaned

def chunk_text(docs, chunk_size=2500, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(docs)

# ---------- Pipeline ----------
def crawl_and_summarize(query: str, use_js=False, k=5):
    if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):
        raise RuntimeError("HUGGINGFACEHUB_API_TOKEN missing (set in .env).")

    print(f"[search] {query}")
    urls = search_links(query, k=k)
    print(f"[found] {len(urls)} urls")
    for u in urls:
        print(" -", u)

    print("[load] fetching pages...")
    docs = load_pages(urls, use_js=use_js)
    print(f"[load] {len(docs)} documents after cleaning")

    if not docs:
        return "No content extracted."

    print("[split] chunking...")
    chunks = chunk_text(docs)

    chain = build_llama3_summarizer_chain()

    # You can summarize each chunk, then combine; or concatenate top chunks.
    print(f"[summarize] {len(chunks)} chunks")
    partial_summaries = []
    for i, ch in enumerate(chunks[:8], start=1):   # limit to first 8 chunks for brevity
        print(f"  - chunk {i}/{min(len(chunks),8)}")
        partial = chain.invoke({"text": ch.page_content[:8000]})
        partial_summaries.append(partial)

    # Final pass to combine partials into a single summary
    combine_chain = build_llama3_summarizer_chain()
    combined_input = "\n\n---\n\n".join(partial_summaries)
    final_summary = combine_chain.invoke({"text": f"Combine and deduplicate the key points below:\n\n{combined_input}"})
    return final_summary

if __name__ == "__main__":
    # Example: change query and use_js as needed
    print(crawl_and_summarize("India announces a plan to launch a “National AI Currency” called A-Rupee in 2026, which will be powered entirely by a government-controlled artificial intelligence system to replace physical cash", use_js=True, k=5))
