from connect import connect_llms
from text_fact import check_fact
from text_summarize import summarize_text
from text_websearch import get_content
from verifiable import verify_summary_against_web

if __name__ == "__main__":
    llms = connect_llms()

    statement1 = "John cena is my favourite wrestler"
    statement2 = "Sun is black"
    statement3 = "Brock Lesnar is best in the world"
    statement4 = "On 09/10/2025 had big accident in Pune between bus and truck"
    statement5 = "India got independence in 1947"
    statement6 = "Brazil won 2022 cricket world cup"
    statement7 = "Africans involved in Delhi bomb blast"
    statement8 = "what were the actual casualties in the New Delhi bomb blast"
    statement9 = "I am big fan of Iron Man Movie"
    statement10 = "15 people died in mumbai bomb blast in 2025"
    
    # print("\nSummarize:", summarize_text(statement))
    # print("\nFact:", check_fact(statement10))
    # print("\nWeb Content:", get_content(statement10))
    # val1=get_content(statement10)
    # print("\nSummarize:", summarize_text(val1))
    sample_web = [
        {"url": "https://aljazeera.example/article", "data": "At 6:52pm a powerful blast occurred near the Red Fort; at least 13 people were killed."}
    ]
    summary = "A car explosion near the Red Fort in Delhi killed 13 people and injured more than 20."
    print(f"final {verify_summary_against_web(sample_web,summary)}")
