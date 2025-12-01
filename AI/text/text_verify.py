from AI.text.text_fact import check_fact
from AI.text.text_websearch import get_content
from AI.text.text_summarize import summarize_text
from AI.text.text_verify_web import verify_summary_against_web

def verify_text(statement):
    summary = summarize_text(statement)
    fact = check_fact(summary)

    if fact and "confidence" in fact and fact["confidence"] < 50:
        webcontent = get_content(summary)
        webverify = verify_summary_against_web(webcontent, summary)
        return webverify

    return fact