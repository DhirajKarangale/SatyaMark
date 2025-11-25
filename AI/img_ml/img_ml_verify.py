import os
import json
from AI.img_ml.inference.detector import detect_ai_image

def test_single_image(path):
    res = detect_ai_image(path)
    print(json.dumps(res, indent=2))


def evaluate_folder(ai_dir, real_dir):
    y_true = []
    y_pred = []

    total_real = 0
    total_ai = 0
    real_correct = 0
    ai_correct = 0

    print("\n Testing REAL images...")
    for f in os.listdir(real_dir):
        p = os.path.join(real_dir, f)
        if not os.path.isfile(p):
            continue

        total_real += 1

        try:
            out = detect_ai_image(p)
            pred = 1 if out["mark"] == "AI" else 0
            y_pred.append(pred)
            y_true.append(0)

            if pred == 0:
                real_correct += 1

            print(f"REAL → Pred: {out['mark']}  {p}")

        except Exception as e:
            print("ERROR (real):", p, e)

    print("\n Testing AI images...")
    for f in os.listdir(ai_dir):
        p = os.path.join(ai_dir, f)
        if not os.path.isfile(p):
            continue

        total_ai += 1

        try:
            out = detect_ai_image(p)
            pred = 1 if out["mark"] == "AI" else 0
            y_pred.append(pred)
            y_true.append(1)

            if pred == 1:
                ai_correct += 1

            print(f"AI → Pred: {out['mark']}  {p}")

        except Exception as e:
            print("ERROR (ai):", p, e)

    # -------------------------------------------------
    # COMPUTE METRICS
    # -------------------------------------------------
    total_real_wrong = total_real - real_correct
    total_ai_wrong = total_ai - ai_correct

    real_accuracy = (real_correct / total_real * 100) if total_real else 0
    ai_accuracy = (ai_correct / total_ai * 100) if total_ai else 0

    total_images = total_real + total_ai
    total_correct = real_correct + ai_correct
    total_wrong = total_images - total_correct
    overall_accuracy = (total_correct / total_images * 100) if total_images else 0

    print("\n==============================")
    print("        FINAL REPORT")
    print("==============================")

    print("\nReal:")
    print(f"  Total:     {total_real}")
    print(f"  Correct:   {real_correct}")
    print(f"  Incorrect: {total_real_wrong}")
    print(f"  Accuracy:  {real_accuracy:.2f}%")

    print("\nAI:")
    print(f"  Total:     {total_ai}")
    print(f"  Correct:   {ai_correct}")
    print(f"  Incorrect: {total_ai_wrong}")
    print(f"  Accuracy:  {ai_accuracy:.2f}%")

    print("\nOverall:")
    print(f"  Total:     {total_images}")
    print(f"  Correct:   {total_correct}")
    print(f"  Incorrect: {total_wrong}")
    print(f"  Accuracy:  {overall_accuracy:.2f}%")

    return {
        "real": {
            "total": total_real,
            "correct": real_correct,
            "incorrect": total_real_wrong,
            "accuracy": real_accuracy,
        },
        "ai": {
            "total": total_ai,
            "correct": ai_correct,
            "incorrect": total_ai_wrong,
            "accuracy": ai_accuracy,
        },
        "overall": {
            "total": total_images,
            "correct": total_correct,
            "incorrect": total_wrong,
            "accuracy": overall_accuracy,
        }
    }


if __name__ == "__main__":
    AI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    TEST_PATH = os.path.join(AI_DIR, "dataset", "test")

    path_ai_1 = os.path.join(TEST_PATH, "ai", "1.jpg")
    path_ai_2 = os.path.join(TEST_PATH, "ai", "5840.jpg")
    path_real_1 = os.path.join(TEST_PATH, "real", "IMG_20220705_123046.jpg")
    path_real_2 = os.path.join(TEST_PATH, "real", "PassPort 2.jpeg")

    test_single_image(path_ai_1)
    # evaluate_folder(TEST_PATH + "/ai", TEST_PATH + "/real")