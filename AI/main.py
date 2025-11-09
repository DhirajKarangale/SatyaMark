from connect import connect_llms, get_llm
from text_factcheck import fact_check
from text_summarize import summarize_text


if __name__ == "__main__":
    llms = connect_llms()

    # summary = summarize_text(
    #     "Le rapport explique la baisse des ventes au T2 et propose trois actions pour le T3."
    # )
    # print("Summary:\n", summary)

    fact = fact_check("I Love mango")
    print("Fact:\n", fact)