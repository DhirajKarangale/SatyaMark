import os
import json
from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from text.utils.parser import clean_text, extract_json

load_dotenv()

BASE_DIR = os.path.dirname(__file__)
JSON_PATH = os.path.join(BASE_DIR, "LLMs.json")

with open(JSON_PATH, "r") as file:
    LLMs = json.load(file)

hf_tokens_env = os.getenv("HF_TOKENS", "")
HF_TOKENS = [t.strip() for t in hf_tokens_env.split(",") if t.strip()]

_current_token_index = 0
_connected_llms = {}  # Format: { token_index: { model_name: llm_instance } }

def _get_llm(name: str, token_index: int):
    if token_index not in _connected_llms:
        _connected_llms[token_index] = {}
        
    if name in _connected_llms[token_index]:
        return _connected_llms[token_index][name]

    cfg = next((item for item in LLMs if item["name"] == name), None)
    if not cfg:
        raise ValueError(f"LLM '{name}' not found in LLMs.json.")

    token = HF_TOKENS[token_index]

    endpoint = HuggingFaceEndpoint(
        task=cfg["task"],
        repo_id=cfg["model_id"],
        provider=cfg.get("provider", "huggingface"),
        do_sample=cfg.get("do_sample", False),
        temperature=cfg.get("temperature", 0.1),
        max_new_tokens=cfg.get("max_new_tokens", 512),
        repetition_penalty=cfg.get("repetition_penalty", 1.03),
        return_full_text=False,
        huggingfacehub_api_token=token,
    )

    if cfg["task"] == "conversational":
        llm = ChatHuggingFace(llm=endpoint)
    else:
        llm = endpoint

    _connected_llms[token_index][name] = llm
    return llm

def invoke(model_names: list[str], prompt: str, parse_as_json: bool = False):
    global _current_token_index
    
    for model_name in model_names:
        attempts_with_different_tokens = 0
        
        while attempts_with_different_tokens < len(HF_TOKENS):
            try:
                llm = _get_llm(model_name, _current_token_index)
                
                response = llm.invoke(prompt)
                if parse_as_json:
                    return extract_json(response)
                else:
                    return clean_text(response)

            except Exception as e:
                error_msg = str(e).lower()
                
                if any(keyword in error_msg for keyword in ["rate limit", "quota", "upgrade", "429", "too many requests"]):
                    print(f"[Warning] Token index {_current_token_index} hit a limit. Rotating token...")
                    _current_token_index = (_current_token_index + 1) % len(HF_TOKENS)
                    attempts_with_different_tokens += 1
                else:
                    print(f"[Error] Model {model_name} failed: {e}. Trying next model...")
                    break
                    
    raise RuntimeError("All models and tokens failed to generate a valid response.")