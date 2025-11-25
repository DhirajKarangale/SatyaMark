import os
from AI.img_forensic.img_forensic_watermark_signature import watermark_analyze
from AI.img_forensic.img_forensic_sensor_fingerprint import sensor_fingerprint_analyze
from AI.img_forensic.img_forensic_gan_artifacts import gan_artifacts_analyze
from AI.img_forensic.img_forensic_gan_artifacts_ml import gan_artifacts_ml_analyze
from AI.img_forensic.img_forensic_local_manipulation import local_manipulation_analyze
from AI.img_forensic.img_forensic_metadata import metadata_analysis
from AI.img_forensic.img_forensic_semantic_consistency import (
    semantic_consistency_analyze,
)
from AI.img_forensic.img_forensic_forensic_decision import classify_image

AI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEST_PATH = os.path.join(AI_DIR, "dataset", "test")


def evaluate_folder(folder_path, expected_label):
    """
    expected_label = "AI" or "NONAI"
    """
    total = 0
    correct = 0

    for file in os.listdir(folder_path):
        if not file.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue

        img_path = os.path.join(folder_path, file)
        total += 1

        # Run the pipeline
        w = watermark_analyze(img_path)
        s = sensor_fingerprint_analyze(img_path)
        g = gan_artifacts_analyze(img_path)
        gml = gan_artifacts_ml_analyze(img_path)
        l = local_manipulation_analyze(img_path)
        m = metadata_analysis(img_path)
        sc = semantic_consistency_analyze(img_path)

        result = classify_image(w, s, g, l, m, sc)

        predicted = result.get("mark", "").upper()

        if predicted == expected_label.upper():
            correct += 1

    incorrect = total - correct
    accuracy = (correct / total * 100) if total > 0 else 0

    return {
        "total": total,
        "correct": correct,
        "incorrect": incorrect,
        "accuracy": accuracy,
    }


def print_block(title, stats):
    print(f"\n{title}:")
    print(f"Total: {stats['total']}")
    print(f"Correct: {stats['correct']}")
    print(f"InCorrect: {stats['incorrect']}")
    print(f"Accuracy: {stats['accuracy']:.2f}%")


def main():
    ai_stats = evaluate_folder(TEST_PATH + "/ai", "AI")
    real_stats = evaluate_folder(TEST_PATH + "/real", "NONAI")

    total = ai_stats["total"] + real_stats["total"]
    correct = ai_stats["correct"] + real_stats["correct"]
    incorrect = ai_stats["incorrect"] + real_stats["incorrect"]
    accuracy = (correct / total * 100) if total > 0 else 0

    overall_stats = {
        "total": total,
        "correct": correct,
        "incorrect": incorrect,
        "accuracy": accuracy,
    }

    print_block("Real Images", real_stats)
    print_block("AI Images", ai_stats)
    print_block("Overall Images", overall_stats)


if __name__ == "__main__":
    main()
