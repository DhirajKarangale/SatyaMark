from summary.summarizer import summarize
from verification.factcheck import fact_check
from verification.verifyability import check_verifyability
from websearch.web_verify import web_verify


def verify_text(statement):
    summary = summarize(statement)

    verifyability = check_verifyability(summary)
    if verifyability and verifyability["mark"] == "UNVERIFYABLE":
        return {"summary": summary, "result": verifyability}

    fact = fact_check(summary)

    if fact and fact["mark"] == "Insufficient":
        webverify = web_verify(summary)
        return {"summary": summary, "result": webverify}

    return {"summary": summary, "result": fact}
