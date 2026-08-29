from utils.huggingface.huggingface import invoke_hf_llm_single_model
from utils.claude.claude import invoke_claude_llm_single_model
import logging

logger = logging.getLogger(__name__)

PROVIDERS_PRIORITY = ["huggingface", "claude"]

def invoke_llm(models: dict, prompt: str, parse_as_json: bool = False):
    """
    Generic LLM router that dispatches calls based on PROVIDERS_PRIORITY.
    It will try Claude first, and fallback to Huggingface if all Claude models fail.
    """
    for provider in PROVIDERS_PRIORITY:
        model_names = models.get(provider, [])
        if not model_names:
            logger.warning(f"No models defined for provider '{provider}'. Skipping to next provider.")
            continue
            
        for model_name in model_names:
            try:
                if provider == "claude":
                    return invoke_claude_llm_single_model(model_name, prompt, parse_as_json)
                elif provider == "huggingface":
                    return invoke_hf_llm_single_model(model_name, prompt, parse_as_json)
                else:
                    logger.warning(f"Unknown provider '{provider}'. Skipping.")
                    continue
            except Exception as e:
                logger.error(f"Model {model_name} (provider: {provider}) failed: {e}. Trying next model...", exc_info=True)
                continue

    raise RuntimeError("All models across all providers failed to generate a valid response.")
