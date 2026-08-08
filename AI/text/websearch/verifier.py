import re
import json
import concurrent.futures
from typing import List, Dict, Any
from utils.huggingface import invoke_llm

MODELS = ["deepseek_r1", "deepseek_v3", "qwen2_5_72b", "llama3_3_70b"]
MAP_MODELS = ["deepseek_v3", "llama3_3_70b", "qwen2_5_72b", "deepseek_r1_distill_llama_8b"]

FORBIDDEN_PHRASES = (
    "provided web evidence",
    "provided web information",
    "given data",
    "given evidence",
    "provided data",
    "provided information",
    "based on the text",
    "the evidence says",
    "according to the evidence",
)


def _sanitize_reason(reason: str) -> str:
    """Removes robotic LLM phrasing to make the reasoning sound like a human journalist."""
    r = reason
    for phrase in FORBIDDEN_PHRASES:
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        r = pattern.sub("publicly reported information", r)
    return r.strip()


def chunk_text(text: str, chunk_size: int = 15000) -> List[str]:
    """Splits large text blocks into manageable chunks to prevent context limits."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def extract_evidence_from_chunk(statement: str, url: str, chunk: str) -> str:
    """The MAP phase: extracts ONLY sentences relevant to the statement."""
    prompt = f"""
You are an evidence extraction system.

STATEMENT:
"{statement}"

TEXT SNIPPET (Source: {url}):
"{chunk}"

TASK:
Extract any specific facts, sentences, or data points from the TEXT SNIPPET that directly prove, disprove, or provide critical context to the STATEMENT.
If you find relevant evidence, you MUST prepend your extraction with the Source URL (e.g., "[{url}]: The article states...").
If there is NO relevant information, output exactly the word "NONE" and nothing else.
Do not explain your reasoning. Just output the extracted evidence or "NONE".
"""
    try:
        # We use MAP_MODELS which are faster and strictly follow instructions
        result = invoke_llm(MAP_MODELS, prompt, parse_as_json=False)
        result = result.strip()
        if result.upper() == "NONE" or result == "":
            return ""
        return result
    except Exception as e:
        print(f"[Warning] Map extraction failed on a chunk: {e}")
        return ""


def fact_check(statement: str, web_data: List[Dict[str, Any]]) -> dict:
    fallback_response = {
        "mark": "Insufficient",
        "confidence": 30,
        "reason": "The system could not confidently process the verification data or insufficient data was provided.",
        "urls": [],
    }

    if not statement or not str(statement).strip() or not web_data:
        print("[Warning] Missing statement or web data. Returning default insufficient response.")
        return fallback_response

    # Prepare chunks for the Map phase with URLs attached
    all_chunks = []
    for item in web_data:
        data = item.get("data", "")
        url = item.get("url", "")
        if len(data) > 50 and url:
            chunks = chunk_text(data)
            for c in chunks:
                all_chunks.append({"url": url, "text": c})

    if not all_chunks:
        print("[Warning] No valid evidence remained after filtering. Returning default insufficient response.")
        return fallback_response

    # 1. MAP PHASE: Run extractions in parallel
    print(f"Running Map phase across {len(all_chunks)} chunk(s)...")
    condensed_evidence = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_chunk = {
            executor.submit(extract_evidence_from_chunk, statement, chunk_data["url"], chunk_data["text"]): chunk_data
            for chunk_data in all_chunks
        }
        
        for future in concurrent.futures.as_completed(future_to_chunk):
            try:
                extracted = future.result()
                if extracted:
                    condensed_evidence.append(extracted)
            except Exception as e:
                print(f"[Warning] Thread execution failed during Map phase: {e}")

    if not condensed_evidence:
        return {
            "mark": "Insufficient",
            "confidence": 80,
            "reason": "After comprehensively scanning all available web evidence, no relevant data could be found regarding this claim.",
            "urls": [item.get("url") for item in web_data if item.get("url")],
        }

    # 2. REDUCE PHASE: Final Verification
    print("Running Reduce phase for final verification...")
    prompt = f"""
You are a professional fact-checking system. 

STATEMENT TO VERIFY:
"{statement}"

CONDENSED EVIDENCE GATHERED FROM THE WEB:
{json.dumps(condensed_evidence, ensure_ascii=False, indent=2)}

TASK:
1. Compare the statement against the evidence. 
2. Ignore any evidence that is irrelevant.
3. Determine whether the statement is Correct, Incorrect, or Insufficient.
   - Mark Correct if the core of the statement is confirmed by the evidence.
   - Mark Incorrect if the evidence explicitly disproves the statement.
   - Mark Insufficient if there isn't enough info to make a call.
4. STRICT GROUNDING RULE: Do NOT use your internal knowledge. You must rely ONLY on the provided EVIDENCE. If the evidence does not contain the answer, you MUST mark it Insufficient.
5. UNIT & MATH RULE: The statement will likely use global SI units. If the scraped evidence uses local/imperial units (or vice versa), you MUST accurately convert and mathematically verify them before making a decision. Do not mark a claim Incorrect simply due to unit differences.
6. NUANCE RULE: If the evidence shows the claim is a mix of true and false (partially true) or requires critical context that is missing from the statement, mark it as Insufficient with a detailed explanation of the nuance rather than forcing a binary Correct/Incorrect.
7. RELEVANCE RULE: Do not discuss irrelevant entities, websites, or data found in the evidence that are unrelated to the core entities of the statement. Keep your reasoning strictly focused on the subject of the claim.
8. URL CITATION RULE: In your JSON output, the "urls" array MUST contain ONLY the precise Source URLs that you actively used to form your reasoning. Do not output all provided URLs.

OUTPUT STRICT JSON ONLY. Do not use Markdown formatting blocks (like ```json).
{{
  "mark": "Correct | Incorrect | Insufficient",
  "confidence": <integer between 0 and 100>,
  "reason": "<Detailed explanation of the reality based on the evidence. Write like a professional journalist.>",
  "urls": ["<list>", "<of>", "<urls>", "<actually>", "<used>", "<in>", "<your>", "<reasoning>"]
}}
"""
    try:
        parsed = invoke_llm(MODELS, prompt, parse_as_json=True)

        if "reason" in parsed and isinstance(parsed["reason"], str):
            parsed["reason"] = _sanitize_reason(parsed["reason"])

        return parsed

    except Exception as e:
        print(f"[Error] Verification failed during Reduce phase: {e}")
        return fallback_response