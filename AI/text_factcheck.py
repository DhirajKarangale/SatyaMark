from connect import get_llm
from marks_of_truth import Marks

def fact_check(text):
    mistral = get_llm("mistral")
    result = mistral.invoke(f"Check this fact is it correct or incorrect: {text}")
    return Marks.CORRECT   