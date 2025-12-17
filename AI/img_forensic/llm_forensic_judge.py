from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from connect import get_llm

llm = get_llm("deepseek_r1_distill_llama_8b")

PROMPT = """
You are a forensic image analyst.

Observed forensic signals:
{signals}

Rules:
- Be conservative
- Do NOT guess
- Prefer false negatives over false positives
- If evidence is mixed or weak, return UNCERTAIN

Return ONLY JSON:
{{
  "mark": "AI" | "NONAI" | "UNCERTAIN",
  "confidence": number,
  "reason": string
}}
"""

prompt = ChatPromptTemplate.from_template(PROMPT)
parser = JsonOutputParser()

def llm_judge(signals: dict):
    signal_text = "\n".join(f"- {k}: {v}" for k, v in signals.items())
    chain = prompt | llm | parser
    return chain.invoke({"signals": signal_text})
