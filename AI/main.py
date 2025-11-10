from connect import connect_llms, get_llm
from text_fact import check_fact
from text_summarize import summarize_text
from text_unverifiable import check_unverifiable

if __name__ == "__main__":
    llms = connect_llms()

    statement = "John cena is my favourite wrestler"

    # print("Summarize:", summarize_text(statement))
    print("\nUnverifiable:", check_unverifiable(statement))
    # print("\nFact:", check_fact(statement))