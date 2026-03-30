import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "text"))
sys.path.append(os.path.join(os.path.dirname(__file__), "img_ml"))
sys.path.append(os.path.join(os.path.dirname(__file__), "img_forensic"))

from text.starter.text_verify import verify_text

# from img_ml_verify import verify_img_ml, evaluate_img_ml, verify_img_ml_url
# from img_forensic_verify import (
#     verify_img_forensic,
#     evaluate_img_forensic,
#     verify_img_forensic_url,
# )

# Text Data
statements = [
  "is recent water in india is because of chemtrail project",
  "i like goku ui",
  "hi i think dk is don",
  "i like to watch comedy movies",
  "I like to eat apples with milk",
  "I like to drink bannana milk with apple shake",
  "I am dkode",
  "i like to watch comedy movies",
  "hi i am don",
  "i like iron name",
  "i like hulk",
  "i like cation america",
  "i like when goku goes in ultra instinct",
  "did iran drops 10 bombs on america?",
  "goku defeated friza"
]


statement = statements[13]

# Image Data
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
TEST_PATH = os.path.join(ROOT_DIR, "dataset", "test")
TRAIN_PATH = os.path.join(ROOT_DIR, "dataset", "train")
TEST_AI_PATH = os.path.join(TEST_PATH, "ai")
TEST_REAL_PATH = os.path.join(TEST_PATH, "real")

path_ai_1 = os.path.join(TEST_AI_PATH, "1.jpg")
path_ai_2 = os.path.join(TEST_AI_PATH, "2.jpg")
path_real_1 = os.path.join(TEST_REAL_PATH, "2.jpg")
path_real_2 = os.path.join(TEST_REAL_PATH, "2.jpg")

image_url = "https://res.cloudinary.com/dfamljkyo/image/upload/v1765866848/v4fh8c9xhegyx2havzar.png"

# Text
print("\n\n\n Text: \n", verify_text(statement))

# Image Forensic
# print(verify_img_forensic(path_real_2))
# print(evaluate_img_forensic(TEST_AI_PATH, TEST_REAL_PATH))
# print(verify_img_forensic_url(image_url))

print("\n \n \n")
