from utils.llm import invoke_llm
import logging

logger = logging.getLogger(__name__)

MODELS = {
    "huggingface": ["deepseek_v3", "llama3_3_70b", "qwen2_5_72b", "deepseek_r1_distill_llama_8b"],
    "claude": ["claude_haiku", "claude_sonnet"]
}

PROMPT_TEMPLATE = """
You are an expert fact-checker. Your task is to analyze the following statement and extract the distinct, independently verifiable factual claims.

If the statement is already a single, atomic claim (e.g. "Apple was founded in 1976"), simply return it as a single-item array.
If the statement contains multiple independent facts (e.g. "Apple was founded in 1976 by Steve Jobs in London"), break it down into an array of separate, self-contained claims.

RULES:
1. Each extracted claim must be a complete sentence that can be fact-checked on its own without needing the original context.
2. Do NOT change the meaning or fix factual errors.
3. If the input is just one simple claim, do not needlessly split it. Return it as is.
4. Return ONLY a valid JSON array of strings. Do not include markdown formatting or explanations.
5. JOURNALISTIC CONTEXT: You are processing text for a legitimate news and fact-checking platform. You will encounter sensitive topics (e.g., natural disasters, missing people, politics). You are authorized and required to process these topics. Do not trigger safety refusals for news events.

Statement:
{text}
"""

def decompose_claims(text: str) -> list[str]:
    if not text or not text.strip():
        return []
        
    try:
        prompt = PROMPT_TEMPLATE.format(text=text)
        result = invoke_llm(MODELS, prompt, parse_as_json=True)
        if isinstance(result, list) and len(result) > 0:
            return [str(c) for c in result]
        return [text]
    except Exception as e:
        logger.warning(f"Failed to decompose claims: {e}")
        return [text]
