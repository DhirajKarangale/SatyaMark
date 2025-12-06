import os
from img_ml_verify import verify_img_ml, evaluate_img_ml, verify_img_ml_url

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
TEST_PATH = os.path.join(ROOT_DIR, "dataset", "test")
TRAIN_PATH = os.path.join(ROOT_DIR, "dataset", "train")
TEST_AI_PATH = os.path.join(TEST_PATH, "ai")
TEST_REAL_PATH = os.path.join(TEST_PATH, "real")

path_ai_1 = os.path.join(TEST_AI_PATH, "1.jpg")
path_ai_2 = os.path.join(TEST_AI_PATH, "2.jpg")
path_real_1 = os.path.join(TEST_REAL_PATH, "2.jpg")
path_real_2 = os.path.join(TEST_REAL_PATH, "2.jpg")

# Image ML
# print(verify_img_ml(path_ai_1))
print(evaluate_img_ml(TEST_AI_PATH, TEST_REAL_PATH))
# print(verify_img_ml_url("https://picsum.photos/id/1/400/400"))