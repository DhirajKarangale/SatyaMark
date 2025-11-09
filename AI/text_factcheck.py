from connect import get_llm
from verdicts import Verdict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = get_llm("deepseek_r1")

prompt_template = """
You are a logical reasoning assistant. Your job is to decide whether a statement is **VERIFIABLE** or **UNVERIFIABLE**.

### Clear definitions:
- **VERIFIABLE** → The statement makes an objective claim that can be confirmed or disproven using facts, evidence, data, or observation.  
  It doesn’t matter whether the claim is *true* or *false* — only that it *can* be fact-checked.

- **UNVERIFIABLE** → The statement expresses an opinion, belief, feeling, personal judgment, or vague generalization that cannot be objectively tested or proven with evidence.

### Examples:
1. "The Sun is blue." → VERIFIABLE (can be checked scientifically — it’s false, but checkable)
2. "Apples have red, green, and yellow colors." → VERIFIABLE (fact-based)
3. "Apple has only red color." → VERIFIABLE (can be proven false with data)
4. "John Cena is my favourite wrestler." → UNVERIFIABLE (subjective preference)
5. "Undertaker is the best wrestler." → UNVERIFIABLE (opinion-based)
6. "Water boils at 100°C at sea level." → VERIFIABLE (scientific measurement)
7. "Chocolate is the most delicious dessert." → UNVERIFIABLE (subjective)
8. "Mumbai is larger than Pune." → VERIFIABLE (can be checked with population data)
9. "I think Mumbai feels more alive than Pune." → UNVERIFIABLE (personal feeling)
10. "Aliens definitely exist somewhere in the universe." → UNVERIFIABLE (no verifiable evidence yet)

---

Now, analyze the following statement carefully and decide:
"{text}"

Respond with **only one word**, exactly:
VERIFIABLE  
or  
UNVERIFIABLE
"""

prompt = ChatPromptTemplate.from_template(prompt_template)
output_parser = StrOutputParser()

def check_unverifiable(text: str) -> Verdict:
    formatted_prompt = prompt.format(text=text)
    chain = llm | output_parser  
    response = chain.invoke(formatted_prompt).strip().upper()

    return response


def fact_check(text):


    return check_unverifiable(text)
