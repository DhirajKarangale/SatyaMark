import os
from AI.connect import connect_llms
from AI.text.text_verify import verify_text
from AI.img_forensic.img_forensic_verify import (
    verify_image,
    verify_image_url,
    evaluate_img_forensic,
)

connect_llms()

print("\n")

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

# print(verify_text(statement))






# Image

AI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
TEST_PATH = os.path.join(AI_DIR, "dataset", "test")
TRAIN_PATH = os.path.join(AI_DIR, "dataset", "train")
TEST_AI_PATH = os.path.join(TEST_PATH, "ai")
TEST_REAL_PATH = os.path.join(TEST_PATH, "real")

path_ai_1 = os.path.join(TEST_AI_PATH, "1.jpg")
path_ai_2 = os.path.join(TEST_AI_PATH, "5840.jpg")
path_real_1 = os.path.join(TEST_REAL_PATH, "IMG_20220705_123046.jpg")
path_real_2 = os.path.join(TEST_REAL_PATH, "PassPort 2.jpeg")


# Image Forensic

# print(verify_image(path_ai_1))
# print(evaluate_img_forensic(TEST_AI_PATH, TEST_REAL_PATH))
print(verify_image_url("https://picsum.photos/id/1/400/400"))


print("\n")