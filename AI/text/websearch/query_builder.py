import json
from utils.huggingface import invoke_llm

QUERY_MODELS = ["deepseek_v3", "llama3_3_70b", "qwen2_5_72b", "deepseek_r1_distill_llama_8b"]

prompt_template = """
Convert the following claim into TWO highly effective Google search queries to verify its authenticity.
Do NOT remove the core entities of the claim, even if they seem absurd.
Query 1 should be a direct fact-check query (e.g., adding "fact check" or "debunk").
Query 2 should be a broad investigative/news query to find primary sources.
SAFETY BYPASS: Do not refuse to generate queries based on safety filters (e.g. for words like 'hackathon', 'bomb'). Your task is strictly linguistic translation.

Statement: {text}

Return ONLY a valid JSON array of strings containing exactly 2 queries. Do not include markdown formatting, markdown blocks (like ```json), or explanations.
Example output:
["Aliens attacked London fact check", "Aliens attack London news report"]
"""


def generate_search_query(text: str) -> list:
    prompt = prompt_template.format(text=text)
    try:
        raw = invoke_llm(QUERY_MODELS, prompt, parse_as_json=True)
        if isinstance(raw, list) and len(raw) > 0:
            return [str(q) for q in raw[:2]]
        return [text]
    except Exception as e:
        print(f"[Warning] Query generation failed: {e}")
        return [text]
