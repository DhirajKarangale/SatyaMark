import re
from utils.huggingface import invoke_llm
from summary.cleaner import clean_raw_social_text
from summary.prompts import (
    get_cleaning_prompt,
    get_semantic_normalization_prompt,
    get_contextual_summarization_prompt,
)

CLEANING_MODELS = ["llama3_1_8b", "qwen2_5_7b", "mistral"]
NORMALIZATION_MODELS = ["deepseek_v3", "qwen2_5_72b", "llama3_3_70b", "deepseek_r1_distill_llama_8b"]
SUMMARIZATION_MODELS = ["deepseek_r1", "deepseek_v3", "llama3_3_70b", "qwen3_32b"]

def llm_clean_text(text: str) -> str:
    if not text:
        return ""
    prompt = get_cleaning_prompt(text)
    try:
        result = invoke_llm(CLEANING_MODELS, prompt, parse_as_json=False)
        return result.strip() if result else text
    except Exception as e:
        print(f"LLM Cleaning failed: {e}")
        return text

def llm_normalize_text(text: str) -> str:
    if not text:
        return ""
    prompt = get_semantic_normalization_prompt(text)
    try:
        result = invoke_llm(NORMALIZATION_MODELS, prompt, parse_as_json=False)
        return result.strip() if result else text
    except Exception as e:
        print(f"LLM Normalization failed: {e}")
        return text

def llm_summarize_text(text: str) -> str:
    if not text:
        return ""
    prompt = get_contextual_summarization_prompt(text)
    try:
        result = invoke_llm(SUMMARIZATION_MODELS, prompt, parse_as_json=False)
        if not result:
            return text

        result = re.sub(
            r"^(summary|compressed summary|here is the summary|output):\s*",
            "",
            result,
            flags=re.IGNORECASE,
        )

        sentences = re.split(r"(?<=[.!?])\s+", result)
        if len(sentences) > 2:
            result = " ".join(sentences[:2]).strip()

        return result
    except Exception as e:
        print(f"LLM Summarization failed: {e}")
        return text.strip()

def summarize(raw_input: str) -> str:
    # Stage 0: Regex based formatting & URL removal
    cleaned_regex = clean_raw_social_text(raw_input)
    if not cleaned_regex:
        return ""

    # Short-circuit logic: If the text is a single concise claim (< 50 words), 
    # DO NOT pass it through LLM summarization. Summarizing short claims destroys proper nouns, grammar context, and precision.
    if len(cleaned_regex.split()) < 50:
        return cleaned_regex

    # Stage 1: LLM Cleaning & Noise Removal
    cleaned_llm = llm_clean_text(cleaned_regex)
    
    if not cleaned_llm or cleaned_llm == cleaned_regex:
        cleaned_llm = cleaned_regex

    # Stage 2: LLM Semantic Normalization & Canonicalization
    normalized_text = llm_normalize_text(cleaned_llm)
    
    if not normalized_text or normalized_text == cleaned_llm:
        normalized_text = cleaned_llm

    # If the text is short enough after normalization, we don't need a heavy summarization step
    # Context Preservation and Ambiguity Reduction is still useful, but if it's <10 words, it's likely already fine.
    if len(normalized_text.split()) < 10:
        return normalized_text
        
    # Stage 3: LLM Context-Preserving Summarization
    final_summary = llm_summarize_text(normalized_text)

    return final_summary
