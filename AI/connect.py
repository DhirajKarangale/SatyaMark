import os
import json
from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

load_dotenv()

with open("LLMs.json", "r") as file:
    LLMs = json.load(file)

# _connected_llms = None
_connected_llms = {}


def connect_llms():
    global _connected_llms
    if _connected_llms is not None:
        return _connected_llms

    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN not found in environment variables.")

    connected_llms = {}

    for cfg in LLMs:

        endpoint = HuggingFaceEndpoint(
            task=cfg["task"],
            repo_id=cfg["model_id"],
            provider=cfg["provider"],
            do_sample=cfg["do_sample"],
            temperature=cfg["temperature"],
            max_new_tokens=cfg["max_new_tokens"],
            repetition_penalty=cfg["repetition_penalty"],
            return_full_text=False,
            huggingfacehub_api_token=hf_token,
        )

        if cfg["task"] == "conversational":
            llm = ChatHuggingFace(llm=endpoint)
        else:
            llm = endpoint

        connected_llms[cfg["name"]] = llm

    _connected_llms = connected_llms
    print(
        f"{len(_connected_llms)} LLMs connected successfully -",
        list(_connected_llms.keys()),
    )
    return _connected_llms


# def get_llm(name: str):
#     llms = connect_llms()
#     if name not in llms:
#         raise ValueError(f"LLM '{name}' not found. Available: {list(llms.keys())}")
#     return llms[name]


def get_llm(name: str):
    if name in _connected_llms:
        return _connected_llms[name]

    cfg = next((c for c in LLMs if c["name"] == name), None)
    if not cfg:
        raise ValueError(f"LLM '{name}' not found in LLMs.json")

    hf_token = os.getenv("HF_TOKEN")
    endpoint = HuggingFaceEndpoint(
        task=cfg["task"],
        repo_id=cfg["model_id"],
        provider=cfg["provider"],
        do_sample=cfg["do_sample"],
        temperature=cfg["temperature"],
        max_new_tokens=cfg["max_new_tokens"],
        repetition_penalty=cfg["repetition_penalty"],
        return_full_text=False,
        huggingfacehub_api_token=hf_token,
    )

    llm = ChatHuggingFace(llm=endpoint) if cfg["task"] == "conversational" else endpoint
    _connected_llms[name] = llm
    print(f"Connected to LLM: {name}")
    return llm
