import re
from connect import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = get_llm("deepseek_r1")

prompt_template = """
You are an expert at converting any claim or statement into a **strong, precise, factual web search query**.

Your output must help the user find **verified information** about what really happened.

Rules:
- If the input is a claim, convert it into a **neutral fact-checking question**.
  Examples:
  - "3 aliens involve in Delhi bomb blast" → "who was actually involved in the Delhi bomb blast"
  - "Aliens attacked London" → "what actually happened in the London attack"
  - "Elon Musk bought Google" → "did Elon Musk buy Google"
  - "There is big car accident in Pune on 10 Nov 2025" → "what happened in the Pune car accident on 10 Nov 2025"
- Remove fictional or impossible details (like aliens) and focus on the **real event**.
- Query can be long if needed — **precision is more important than length**.
- DO NOT include any reasoning, tags, or explanations.  
- Return only the final query string.

Statement:
{text}

Return ONLY the rewritten search query.
"""

prompt = ChatPromptTemplate.from_template(prompt_template)
output_parser = StrOutputParser()


def search_query(text: str):
    response = (prompt | llm | output_parser).invoke({"text": text})

    raw = str(response)
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL | re.IGNORECASE)
    raw = re.sub(r"</?think>", "", raw, flags=re.IGNORECASE)

    lines = [line.strip() for line in raw.split("\n") if line.strip()]
    if not lines:
        return ""

    final = lines[-1]  
    final = final.strip().strip('"').strip("'").strip("`")
    final = re.sub(r"\s+", " ", final).strip()

    return final
