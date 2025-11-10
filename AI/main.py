from connect import connect_llms, get_llm
from text_fact import check_fact
from text_summarize import summarize_text
from text_unverifiable import check_unverifiable

if __name__ == "__main__":
    llms = connect_llms()

    statement1 = "John cena is my favourite wrestler"
    statement2 = "Sun is black"
    statement3 = "Brock Lesnar is best in the world"
    statement4 = "On 09/10/2025 had big accident in Pune between bus and truck"
    statement5 = "India got independence in 1905"

    # print("\nSummarize:", summarize_text(statement))
    # print("\nUnverifiable:", check_unverifiable(statement3))
    print("\nFact:", check_fact(statement5))
    print("\n\n")
