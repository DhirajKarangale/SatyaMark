from text_fact import fact_check
from text_websearch import get_content
from text_summarize import clean_and_summarize
from text_verifyability import check_verifyability
from text_verify_web import fact_check_with_web

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
        webcontent = get_content(summary)
        # log(webcontent, "web_data")
        webverify = fact_check_with_web(summary, webcontent)
        return webverify

    return fact


def verify_text_summary(statement):
    summary = clean_and_summarize(statement)

    verifyability = check_verifyability(summary)
    if verifyability and verifyability["mark"] == "UNVERIFYABLE":
        return {"summary": summary, "result": verifyability}

    fact = fact_check(summary)

    if fact and fact["mark"] == "Insufficient":
        webcontent = get_content(summary)
        webverify = fact_check_with_web(summary, webcontent)
        return {"summary": summary, "result": webverify}

    return {"summary": summary, "result": fact}
