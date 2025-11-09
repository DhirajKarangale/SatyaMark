from connect import get_llm

def fact_check(text):
    mistral = get_llm("mistral")
    result = mistral.invoke(f"Check this fact is it correct or incorrect: {text}")
    return result   