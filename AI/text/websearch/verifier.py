import json
from typing import List, Dict
from text.utils.huggingface import invoke

MODELS = ["deepseek_r1", "deepseek_v3", "qwen2_5"]


def fact_check(statement: str, verified_data: List[Dict]) -> dict:
    prompt = f"""
You are an expert fact-checking system. Analyze the statement against the provided web evidence.

STATEMENT: "{statement}"

EVIDENCE:
{json.dumps(verified_data, ensure_ascii=False, indent=2)}

INSTRUCTIONS:
1. Determine if the statement is Correct, Incorrect, or Insufficient based ONLY on the evidence.
2. If the evidence says "Scraping blocked", rely on the provided Search Engine Snippet.
3. If the evidence does not contain enough info, output Insufficient.

Output your response in STRICT JSON format like this:
{{
  "mark": "Correct", 
  "confidence": 90,
  "reason": "Clear explanation of why...",
  "urls": ["https://example.com"]
}}
"""
    try:
        parsed = invoke(MODELS, prompt, parse_as_json=True)
        return parsed
    except Exception as e:
        return {
            "mark": "Insufficient",
            "confidence": 30,
            "reason": "System failed to confidently parse the verification data.",
            "urls": [],
        }
