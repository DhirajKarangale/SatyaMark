from utils.llm import invoke_llm
import logging

logger = logging.getLogger(__name__)

MODELS = {
    "huggingface": ["deepseek_v3", "llama3_3_70b", "qwen2_5_72b", "deepseek_r1_distill_llama_8b"],
    "claude": ["claude_haiku", "claude_sonnet"]
}

PROMPT_TEMPLATE = """
You are a factual context analysis engine. Your task is to analyze the following statement and extract its verification context.

This context will be used by a downstream fact-checker to ensure it aligns the scope of evidence properly with the scope of the claim.

Analyze the claim and output a JSON object with exactly the following keys:
- "temporal_scope": Describe the temporal nature of the claim (e.g., "Timeless/General", "Specific Date: [date]", "Recent Past", "Future Prediction").
- "claim_nature": Describe the nature of the claim (e.g., "General Pattern", "Specific Event", "Statistical Metric", "Scientific Fact").
- "evidence_requirements": Describe what kind of evidence is required to prove or disprove this claim, and explicitly note if evidence of a single specific event is insufficient to disprove a general pattern.

Return ONLY a valid JSON object. Do not include markdown formatting or explanations.

Statement:
{text}
"""

def analyze_context(text: str) -> dict:
    if not text or not text.strip():
        return {
            "temporal_scope": "Unknown",
            "claim_nature": "Unknown",
            "evidence_requirements": "Unknown"
        }
        
    try:
        prompt = PROMPT_TEMPLATE.format(text=text)
        result = invoke_llm(MODELS, prompt, parse_as_json=True)
        
        if isinstance(result, dict):
             return {
                 "temporal_scope": str(result.get("temporal_scope", "Unknown")),
                 "claim_nature": str(result.get("claim_nature", "Unknown")),
                 "evidence_requirements": str(result.get("evidence_requirements", "Unknown"))
             }
        
    except Exception as e:
        logger.warning(f"Failed to analyze context: {e}")
        
    return {
        "temporal_scope": "Unknown",
        "claim_nature": "Unknown",
        "evidence_requirements": "Unknown"
    }
