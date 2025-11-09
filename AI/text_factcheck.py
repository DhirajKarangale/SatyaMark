from connect import get_llm
from verdicts import Verdict

def fact_check(text):
    mistral = get_llm("mistral")
    result = mistral.invoke(f"Check this fact is it correct or incorrect: {text}")
    return Verdict.CORRECT   