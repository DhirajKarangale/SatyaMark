from text.utils.huggingface import invoke_llm

QUERY_MODELS = ["deepseek_r1", "deepseek_v3", "qwen2_5", "llama3"]

prompt_template = """
Convert the following claim into a highly effective Google search query to verify its authenticity.
Do NOT remove the core entities of the claim, even if they seem absurd.
Instead, formulate a query that will surface fact-checks or news reports about this specific claim.

Examples:
- "Aliens attacked London" → "Aliens attacked London fact check news"
- "Elon Musk bought Google" → "Did Elon Musk buy Google news"

Statement: {text}

Return ONLY the rewritten search query string. No quotes, no explanations.
"""


def generate_search_query(text: str) -> str:
    prompt = prompt_template.format(text=text)
    try:
        raw = invoke_llm(QUERY_MODELS, prompt, parse_as_json=False)
        lines = [line.strip() for line in raw.split("\n") if line.strip()]
        if not lines:
            return text
        final = lines[-1].strip().strip('"').strip("'").strip("`")
        return final
    except Exception as e:
        print(f"[Warning] Query generation failed: {e}")
        return text
