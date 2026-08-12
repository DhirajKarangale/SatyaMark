import re
from utils.llm import invoke_llm
from summary.cleaner import clean_raw_social_text
from summary.prompts import (
    get_cleaning_prompt,
    get_semantic_normalization_prompt,
    get_contextual_summarization_prompt,
)
import logging

logger = logging.getLogger(__name__)

CLEANING_MODELS = {
    "huggingface": ["llama3_1_8b", "qwen2_5_7b", "mistral"],
    "claude": ["claude_haiku", "claude_sonnet"]
}
NORMALIZATION_MODELS = {
    "huggingface": ["deepseek_v3", "qwen2_5_72b", "llama3_3_70b", "deepseek_r1_distill_llama_8b"],
    "claude": ["claude_haiku", "claude_sonnet"]
}
SUMMARIZATION_MODELS = {
    "huggingface": ["deepseek_r1", "deepseek_v3", "llama3_3_70b", "qwen3_32b"],
    "claude": ["claude_haiku", "claude_sonnet"]
}

def llm_clean_text(text: str) -> str:
    if not text:
        return ""
    prompt = get_cleaning_prompt(text)
    try:
        result = invoke_llm(CLEANING_MODELS, prompt, parse_as_json=False)
        return result.strip() if result else text
    except Exception as e:
        logger.error(f"LLM Cleaning failed: {e}", exc_info=True)
        return text

def llm_normalize_text(text: str) -> str:
    if not text:
        return ""
    prompt = get_semantic_normalization_prompt(text)
    try:
        result = invoke_llm(NORMALIZATION_MODELS, prompt, parse_as_json=False)
        return result.strip() if result else text
    except Exception as e:
        logger.error(f"LLM Normalization failed: {e}", exc_info=True)
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
        logger.error(f"LLM Summarization failed: {e}", exc_info=True)
        return text.strip()

def summarize(raw_input: str) -> str:
    cleaned_regex = clean_raw_social_text(raw_input)
    if not cleaned_regex:
        return ""

    # We removed the 50-word check so that short texts still go through the LLM for deduplication.

    cleaned_llm = llm_clean_text(cleaned_regex)
    
    if not cleaned_llm or cleaned_llm == cleaned_regex:
        cleaned_llm = cleaned_regex

    normalized_text = llm_normalize_text(cleaned_llm)
    
    if not normalized_text or normalized_text == cleaned_llm:
        normalized_text = cleaned_llm

    if len(normalized_text.split()) < 10:
        return normalized_text
        
    final_summary = llm_summarize_text(normalized_text)

    return final_summary
