from text.verification.factcheck import fact_check
from text.summary.summarizer import clean_and_summarize
from text.verification.verifyability import check_verifyability
from text.websearch.web_verify import web_verify

LOG_FILE = "text_verification_log.txt"


def log(data, title=None):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 80 + "\n")
        if title:
            f.write(f"{title}:\n")
        f.write(str(data) + "\n")


def verify_text(statement):
    summary = clean_and_summarize(statement)
    verifyability = check_verifyability(summary)

    if verifyability and verifyability["mark"] == "UNVERIFYABLE":
        return verifyability

    # log(summary, "text")
    fact = fact_check(summary)

    if fact and fact["mark"] == "Insufficient":
        webverify = web_verify(summary)
        return webverify

    return fact


def verify_text_summary(statement):
    summary = clean_and_summarize(statement)

    verifyability = check_verifyability(summary)
    if verifyability and verifyability["mark"] == "UNVERIFYABLE":
        return {"summary": summary, "result": verifyability}

    fact = fact_check(summary)

    if fact and fact["mark"] == "Insufficient":
        webverify = web_verify(summary)
        return {"summary": summary, "result": webverify}

    return {"summary": summary, "result": fact}
