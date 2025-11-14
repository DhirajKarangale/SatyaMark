from connect import connect_llms
from text_fact import check_fact
from text_summarize import summarize_text
from text_subjective import check_subjective
from websearch_query import get_query
from websearch_content import get_content

if __name__ == "__main__":
    llms = connect_llms()

    statement1 = "John cena is my favourite wrestler"
    statement2 = "Sun is black"
    statement3 = "Brock Lesnar is best in the world"
    statement4 = "On 09/10/2025 had big accident in Pune between bus and truck"
    statement5 = "India got independence in 1905"
    statement6 = "Brazil won 2022 cricket world cup"
    statement7 = "Africans involved in Delhi bomb blast"
    statement8 = "what were the actual casualties in the New Delhi bomb blast"

    # print("\nSummarize:", summarize_text(statement))
    # print("\nSubjective:", check_subjective(statement3))
    print("\nFact:", check_fact(statement4))
    # print("\nQuery:", get_query(statement7))
    # print("\nWeb Content:", get_content(statement8))

    print("\n") 
