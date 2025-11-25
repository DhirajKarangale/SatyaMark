import os
from AI.img_forensic.img_forensic_watermark_signature import watermark_analyze
from AI.img_forensic.img_forensic_sensor_fingerprint import sensor_fingerprint_analyze
from AI.img_forensic.img_forensic_gan_artifacts import gan_artifacts_analyze
from AI.img_forensic.img_forensic_gan_artifacts_ml import gan_artifacts_ml_analyze
from AI.img_forensic.img_forensic_local_manipulation import local_manipulation_analyze
from AI.img_forensic.img_forensic_metadata import metadata_analysis
from AI.img_forensic.img_forensic_semantic_consistency import semantic_consistency_analyze
from AI.img_forensic.img_forensic_forensic_decision import classify_image

AI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEST_PATH = os.path.join(AI_DIR, "dataset", "test")

path_ai_1 = os.path.join(TEST_PATH, "ai", "1.jpg")
path_ai_2 = os.path.join(TEST_PATH, "ai", "5840.jpg")
path_real_1 = os.path.join(TEST_PATH, "real", "IMG_20220705_123046.jpg")
path_real_2 = os.path.join(TEST_PATH, "real", "PassPort 2.jpeg")

image_path = path_ai_1

watermark_output = watermark_analyze(image_path)
sensor_output = sensor_fingerprint_analyze(image_path)
gan_output = gan_artifacts_analyze(image_path)
gan_output_ml = gan_artifacts_ml_analyze(image_path)
local_output = local_manipulation_analyze(image_path)
metadata_output = metadata_analysis(image_path)
semantic_output = semantic_consistency_analyze(image_path)


print("\n")

# print(open("E:\\FullStack\\SatyaMark\\AI\\img_forensic\\img_forensic_semantic_consistency.py").read()[560:650])


# print("Watermark: ", watermark_output)
# print("Sensor Fingerprint: ", sensor_output)
# print("Gan Artifacts: ", gan_output)
# print("Gan Artifacts: ", gan_output_ml)
# print("Local Manipulation: ", local_output)
# print("Metadata: ", metadata_output)
# print("Semantic Consistency: ", semantic_output)

result = classify_image(
    watermark_output,
    sensor_output,
    gan_output,
    local_output,
    metadata_output,
    semantic_output,
)

print(result)

print("\n")