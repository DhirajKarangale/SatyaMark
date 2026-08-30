import re
import json
import concurrent.futures
from typing import List, Dict, Any
from utils.llm import invoke_llm
import logging
import time
from utils.tracer import trace_event

logger = logging.getLogger(__name__)

MODELS = {
    "huggingface": ["deepseek_r1", "deepseek_v3", "qwen2_5_72b", "llama3_3_70b"],
    "claude": ["claude_haiku", "claude_sonnet"]
}
MAP_MODELS = {
    "huggingface": ["deepseek_v3", "llama3_3_70b", "qwen2_5_72b", "deepseek_r1_distill_llama_8b"],
    "claude": ["claude_haiku", "claude_sonnet"]
}

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
        start_time = time.time()
        result = invoke_llm(MAP_MODELS, prompt, parse_as_json=False)
        duration = int((time.time() - start_time) * 1000)
        
        result = result.strip()
        if result.upper() == "NONE" or result == "":
            trace_event("python_ai_worker", "evidence_processing", "map_extraction", duration_ms=duration, details={"url": url, "statement": statement, "chunk_length": len(chunk), "relevance": "irrelevant", "extracted_evidence": "NONE"})
            return ""
        
        trace_event("python_ai_worker", "evidence_processing", "map_extraction", duration_ms=duration, details={"url": url, "statement": statement, "chunk_length": len(chunk), "relevance": "relevant", "extracted_evidence": result})
        return result
    except Exception as e:
        duration = int((time.time() - start_time) * 1000) if 'start_time' in locals() else None
        trace_event("python_ai_worker", "evidence_processing", "map_extraction", status="failed", duration_ms=duration, details={"url": url, "error": str(e)})
        logger.warning(f"Map extraction failed on a chunk: {e}", exc_info=True)
        return ""


def fact_check(statement: str, web_data: List[Dict[str, Any]]) -> dict:
    fallback_response = {
        "mark": "Insufficient",
        "confidence": 30,
        "reason": "The system could not confidently process the verification data or insufficient data was provided.",
        "urls": [],
    }

    if not statement or not str(statement).strip() or not web_data:
        logger.warning("Missing statement or web data. Returning default insufficient response.")
        return fallback_response

    all_chunks = []
    for item in web_data:
        data = item.get("data", "")
        url = item.get("url", "")
        if len(data) > 50 and url:
            chunks = chunk_text(data)
            trace_event("python_ai_worker", "evidence_processing", "chunking_details", details={"url": url, "original_length": len(data), "num_chunks": len(chunks), "chunk_size": 15000})
            for c in chunks:
                all_chunks.append({"url": url, "text": c})

    if not all_chunks:
        logger.warning("No valid evidence remained after filtering. Returning default insufficient response.")
        return fallback_response

    logger.info(f"Running Map phase across {len(all_chunks)} chunk(s)...")
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
                logger.warning(f"Thread execution failed during Map phase: {e}", exc_info=True)

    if not condensed_evidence:
        return {
            "mark": "Insufficient",
            "confidence": 80,
            "reason": "After comprehensively scanning all available web evidence, no relevant data could be found regarding this claim.",
            "urls": [item.get("url") for item in web_data if item.get("url")],
        }

    url_weights = {item.get("url"): item.get("credibility_weight", 1.0) for item in web_data if item.get("url")}

    logger.info("Running Reduce phase for final verification...")
    prompt = f"""
You are a professional fact-checking system. 

STATEMENT TO VERIFY:
"{statement}"

CONDENSED EVIDENCE GATHERED FROM THE WEB:
{json.dumps(condensed_evidence, ensure_ascii=False, indent=2)}

SOURCE CREDIBILITY WEIGHTS:
{json.dumps(url_weights, indent=2)}

TASK:
1. Compare the statement against the evidence. 
2. Determine whether the statement is Correct, Incorrect, or Insufficient based ONLY on the evidence.
3. MUTUALLY EXCLUSIVE CAUSE RULE (CRITICAL): If the statement claims Event X is caused by Y (e.g. "floods due to rain"), but the evidence conclusively proves Event X is caused by Z (e.g. "floods due to glacier collapse"), you MUST mark the statement as 'Incorrect'. Do NOT mark it 'Insufficient'.
4. STRICT GROUNDING RULE: Do NOT use your internal knowledge. If the evidence does not contain the answer, mark it Insufficient.
5. CREDIBILITY RULE: Use the SOURCE CREDIBILITY WEIGHTS to resolve conflicts. Trust higher-weighted sources.
6. UNIT & MATH RULE: Accurately convert and mathematically verify units before making a decision.
7. NUANCE RULE: If the evidence shows the claim is a mix of true and false, mark it as Insufficient with a detailed explanation of the nuance.
8. RELEVANCE RULE: Do not discuss irrelevant entities. Keep your reasoning strictly focused on the subject of the claim.
9. URL CITATION RULE: In your JSON output, the "urls" array MUST contain ONLY the precise Source URLs that you actively used to form your reasoning.

OUTPUT STRICT JSON ONLY. Do not use Markdown formatting blocks (like ```json).
{{
  "mark": "Correct | Incorrect | Insufficient",
  "confidence": <integer between 0 and 100>,
  "reason": "<Detailed explanation of the reality based on the evidence. Write like a professional journalist.>",
  "urls": ["<list>", "<of>", "<urls>", "<actually>", "<used>", "<in>", "<your>", "<reasoning>"]
}}
"""
    try:
        start_time = time.time()
        parsed = invoke_llm(MODELS, prompt, parse_as_json=True)
        duration = int((time.time() - start_time) * 1000)

        if "reason" in parsed and isinstance(parsed["reason"], str):
            parsed["reason"] = _sanitize_reason(parsed["reason"])

        trace_event("python_ai_worker", "evidence_processing", "reduce_fact_check", duration_ms=duration, details={"statement": statement, "num_evidence": len(condensed_evidence), "output": parsed})
        return parsed

    except Exception as e:
        duration = int((time.time() - start_time) * 1000) if 'start_time' in locals() else None
        trace_event("python_ai_worker", "evidence_processing", "reduce_fact_check", status="failed", duration_ms=duration, details={"statement": statement, "error": str(e)})
        logger.error(f"Verification failed during Reduce phase: {e}", exc_info=True)
        return fallback_response