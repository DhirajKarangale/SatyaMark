import json, re
from connect import get_llm
from marks_of_truth import Marks
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = get_llm("deepseek_r1")

prompt_template = """
You are a logical reasoning assistant. Your task is to decide whether a statement is **VERIFIABLE** or **UNVERIFIABLE**, and briefly explain why if it is UNVERIFIABLE.

### Definitions:
- **VERIFIABLE** → The statement makes an objective claim that can be confirmed or disproven using facts, evidence, data, or observation.  
  It doesn't matter whether it's true or false — only that it *can* be checked objectively.
- **UNVERIFIABLE** → The statement is based on personal opinion, belief, feeling, or vague/generalized judgment that cannot be tested objectively.

### Examples:
1. "The Sun is blue."  
   → **Classification:** VERIFIABLE  
   → **Reason:** (skip reason because it's verifiable)

2. "John Cena is my favourite wrestler."  
   → **Classification:** UNVERIFIABLE  
   → **Reason:** It's a personal preference, not an objective fact.

3. "Apple has only red color."  
   → **Classification:** VERIFIABLE  
   → **Reason:** (skip reason because it's verifiable)

4. "Undertaker is the best wrestler."  
   → **Classification:** UNVERIFIABLE  
   → **Reason:** “Best” is subjective and depends on personal opinion.

---

Now analyze the following statement:
"{text}"

Respond **strictly** in this JSON format:
{{
  "classification": "VERIFIABLE" or "UNVERIFIABLE",
  "reason": "<short reason only if UNVERIFIABLE, otherwise empty>"
}}
Do not include any explanation, chain-of-thought, or tags like <THINK>.
"""

prompt = ChatPromptTemplate.from_template(prompt_template)
output_parser = StrOutputParser()


def check_unverifiable(text: str):
    formatted_prompt = prompt.format(text=text)
    chain = llm | output_parser
    raw_response = chain.invoke(formatted_prompt).strip()

    raw_response = re.sub(
        r"<THINK>.*?</THINK>", "", raw_response, flags=re.DOTALL
    ).strip()

    json_match = re.search(r"\{[\s\S]*?\}", raw_response)
    classification, reason = "", ""

    if json_match:
        json_str = json_match.group(0)
        try:
            parsed = json.loads(json_str)
            classification = parsed.get("classification", "").strip().upper()
            reason = parsed.get("reason", "").strip()
        except json.JSONDecodeError:
            cls_match = re.search(
                r'"?classification"?\s*[:=]\s*"?(\w+)"?', json_str, re.I
            )
            rsn_match = re.search(r'"?reason"?\s*[:=]\s*"?([^"}]+)"?', json_str, re.I)
            if cls_match:
                classification = cls_match.group(1).upper()
            if rsn_match:
                reason = rsn_match.group(1).strip()
    else:
        classification = (
            "UNVERIFIABLE" if "UNVERIFIABLE" in raw_response.upper() else "VERIFIABLE"
        )

    mark = Marks.UNVERIFIABLE if "UNVERIFIABLE" in classification else Marks.VERIFIABLE

    return {
        "mark": mark,
        "reason": reason if mark == Marks.UNVERIFIABLE else "",
    }
