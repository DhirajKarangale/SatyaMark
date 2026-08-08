import os
import json
import time
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

BASE_DIR = os.path.dirname(__file__)
JSON_PATH = os.path.join(BASE_DIR, "LLMs_claude.json")

with open(JSON_PATH, "r") as file:
    LLMs = json.load(file)

anthropic_keys_env = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_KEYS = [t.strip() for t in anthropic_keys_env.split(",") if t.strip()]

MAX_RETRIES = int(os.getenv("EXPONENTIAL_BACKOFF_MAX_RETRIES", "3"))
BASE_TIME = int(os.getenv("EXPONENTIAL_BACKOFF_BASE_TIME", "2"))

_current_claude_key_index = 0
_connected_claude_llms = {}

def _get_claude_llm(name: str, key_index: int):
    if key_index not in _connected_claude_llms:
        _connected_claude_llms[key_index] = {}

    if name in _connected_claude_llms[key_index]:
        return _connected_claude_llms[key_index][name]

    cfg = next((item for item in LLMs if item["name"] == name), None)
    if not cfg:
        raise ValueError(f"LLM '{name}' not found in LLMs.json.")
        
    if not ANTHROPIC_KEYS:
        raise ValueError("ANTHROPIC_API_KEY is not set in environment.")

    api_key = ANTHROPIC_KEYS[key_index]

    from langchain_anthropic import ChatAnthropic
    
    kwargs = {
        "model": cfg["model_id"],
        "max_tokens": cfg.get("max_new_tokens", 4096),
        "api_key": api_key,
    }
    
    if "temperature" in cfg:
        kwargs["temperature"] = cfg["temperature"]
        
    llm = ChatAnthropic(**kwargs)

    _connected_claude_llms[key_index][name] = llm
    return llm

def invoke_claude_llm_single_model(model_name: str, prompt: str, parse_as_json: bool = False):
    global _current_claude_key_index
    attempts_with_different_keys = 0

    while attempts_with_different_keys < max(1, len(ANTHROPIC_KEYS)):
        network_retries = 0
        
        while network_retries <= MAX_RETRIES:
            try:
                llm = _get_claude_llm(model_name, _current_claude_key_index)

                response = llm.invoke(prompt)
                if parse_as_json:
                    from utils.parser import extract_json
                    return extract_json(response)
                else:
                    from utils.parser import clean_text
                    return clean_text(response)

            except Exception as e:
                error_msg = str(e).lower()

                limit_keywords = [
                    "rate limit",
                    "quota",
                    "upgrade",
                    "429",
                    "too many requests",
                    "402",
                    "payment required",
                    "depleted",
                    "credits",
                    "401",
                    "unauthorized",
                    "expired",
                    "invalid token",
                    "overloaded"
                ]

                if any(keyword in error_msg for keyword in limit_keywords) and len(ANTHROPIC_KEYS) > 1:
                    logger.warning(
                        f"Claude Key index {_current_claude_key_index} hit a limit or expired. Rotating key..."
                    )
                    _current_claude_key_index = (_current_claude_key_index + 1) % len(ANTHROPIC_KEYS)
                    attempts_with_different_keys += 1
                    break
                elif any(keyword in error_msg for keyword in limit_keywords):
                     logger.error("Claude Key hit a limit, but no fallback keys are available.", exc_info=True)
                     raise RuntimeError(f"Claude API limits reached: {e}")
                else:
                    network_retries += 1
                    if network_retries <= MAX_RETRIES:
                        delay = BASE_TIME ** network_retries
                        logger.warning(
                            f"Claude Model {model_name} network/timeout error: {e}. Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"Claude Model {model_name} failed after {MAX_RETRIES} network retries: {e}.", exc_info=True
                        )
                        raise RuntimeError(f"Claude Model {model_name} failed after {MAX_RETRIES} network retries: {e}")

    raise RuntimeError(f"All Claude keys exhausted for model {model_name}.")
