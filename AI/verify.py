from AI.connect import connect_llms
from AI.text.text_verify import verify_text

connect_llms()

# Text
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
statement = statement4

print(verify_text(statement))


