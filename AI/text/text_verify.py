from text_fact import fact_check
from text_websearch import get_content
from text_summarize import summarize_text
from text_verifyability import check_verifyability
from text_verify_web import fact_check_with_web


def verify_text(statement):
    summary = summarize_text(statement)
    verifyability = check_verifyability(summary)

    if verifyability and verifyability["mark"] == "UNVERIFYABLE":
        return verifyability

    fact = fact_check(summary)

    if fact and fact["mark"] == "Insufficient":
        webcontent = get_content(summary)
        webverify = fact_check_with_web(summary, webcontent)
        return webverify

    return fact


def verify_text_summary(statement):
    summary = summarize_text(statement)

    verifyability = check_verifyability(summary)
    if verifyability and verifyability["mark"] == "UNVERIFYABLE":
        return {"summary": summary, "result": verifyability}

    fact = fact_check(summary)

    if fact and fact["mark"] == "Insufficient":
        webcontent = get_content(summary)
        webverify = fact_check_with_web(summary, webcontent)
        return {"summary": summary, "result": webverify}

    return {"summary": summary, "result": fact}
