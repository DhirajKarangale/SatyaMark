import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "text"))
sys.path.append(os.path.join(os.path.dirname(__file__), "img_ml"))
sys.path.append(os.path.join(os.path.dirname(__file__), "img_forensic"))

from text_verify import verify_text
from img_ml_verify import verify_img_ml, evaluate_img_ml, verify_img_ml_url
from img_forensic_verify import (
    verify_img_forensic,
    evaluate_img_forensic,
    verify_img_forensic_url,
)

print("\n")

# Text Data
statement1 = "The Great Wall of China is located in China."
statement2 = "The Eiffel Tower is located in Germany."
statement3 = "In the grand tapestry of human innovation, renewable energy stands as a beacon of sustainable progress."
statement4 = "NASA will announce evidence of alien life in 2030."
statement5 = "Chocolate ice cream is the best flavor ever."
statement6 = "The committee approved the proposal yesterday."
statement = statement1

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
# print(verify_text(statement))

# Image Forensic
# print(verify_img_forensic(path_real_2))
print(evaluate_img_forensic(TEST_AI_PATH, TEST_REAL_PATH))
# print(verify_img_forensic_url(image_url))

# Image ML
# print(verify_img_ml(path_ai_1))
# print(evaluate_img_ml(TEST_AI_PATH, TEST_REAL_PATH))
# print(verify_img_ml_url(image_url))

print("\n")
