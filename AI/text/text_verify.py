from text_fact import check_fact
from text_websearch import get_content
from text_summarize import summarize_text
from text_verifyability import check_verifyability
from text_verify_web import verify_summary_against_web


def verify_text(statement):
    summary = summarize_text(statement)
    verifyability = check_verifyability(summary)
    return verifyability
    # fact = check_fact(summary)

    # if fact and "confidence" in fact and fact["confidence"] < 50:
    #     webcontent = get_content(summary)
    #     webverify = verify_summary_against_web(webcontent, summary)
    #     return webverify

    # return fact
