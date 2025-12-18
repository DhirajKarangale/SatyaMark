from text_fact import fact_check
from text_websearch import get_content
from text_summarize import summarize_text
from text_verifyability import check_verifyability
from text_verify_web import verify_summary_against_web


def verify_text(statement):
    summary = summarize_text(statement)
    verifyability = check_verifyability(summary)
    if (verifyability and verifyability["mark"] == "UNVERIFYABLE"):
        return verifyability
    fact = fact_check(summary)

    if False and fact and fact["mark"] == "Insufficient":
        webcontent = get_content(summary)
        # webverify = verify_summary_against_web(webcontent, summary)
        return webcontent

    return fact
