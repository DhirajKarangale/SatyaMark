import os
import imghdr
import requests
import tempfile
from PIL import Image
from urllib.parse import urlparse

from AI.img_ml.inference.detector import detect_ai_image


def verify_img_ml(image_path: str):
    """Run ML-based AI classifier on a local image file."""
    try:
        return detect_ai_image(image_path)
    except Exception as e:
        return {"error": str(e)}


def verify_img_ml_url(url: str, timeout: int = 10, max_bytes: int = 5 * 1024 * 1024):
    """Validate URL, download image, run ML-based classifier."""
    
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return {"error": "Invalid URL"}
    except:
        return {"error": "Invalid URL"}

    temp_path = None

    try:
        resp = requests.get(url, stream=True, timeout=timeout)
        resp.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            temp_path = tmp.name
            size = 0

            for chunk in resp.iter_content(8192):
                if not chunk:
                    break

                size += len(chunk)
                if size > max_bytes:
                    return {"error": "File too large (>5MB)"}

                tmp.write(chunk)

        kind = imghdr.what(temp_path)
        if kind is None:
            try:
                with Image.open(temp_path) as im:
                    im.verify()
            except:
                return {"error": "Downloaded file is not an image"}

        return verify_img_ml(temp_path)

    except Exception as e:
        return {"error": str(e)}

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


def evaluate_img_ml(ai_folder: str, real_folder: str):
    """Evaluate ML classifier accuracy on AI and Real datasets (folders)."""

    def eval_folder(folder_path, expected_label):
        total = 0
        correct = 0

        for file in os.listdir(folder_path):
            if not file.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue

            img_path = os.path.join(folder_path, file)
            total += 1

            result = verify_img_ml(img_path)
            predicted = result.get("mark", "").upper()

            if predicted == expected_label.upper():
                correct += 1

        incorrect = total - correct
        accuracy = (correct / total * 100) if total else 0

        return {
            "total": total,
            "correct": correct,
            "incorrect": incorrect,
            "accuracy": accuracy,
        }

    ai_stats = eval_folder(ai_folder, "AI")
    real_stats = eval_folder(real_folder, "NONAI")

    total = ai_stats["total"] + real_stats["total"]
    correct = ai_stats["correct"] + real_stats["correct"]
    incorrect = ai_stats["incorrect"] + real_stats["incorrect"]
    accuracy = (correct / total * 100) if total else 0

    return {
        "ai": ai_stats,
        "real": real_stats,
        "overall": {
            "total": total,
            "correct": correct,
            "incorrect": incorrect,
            "accuracy": accuracy,
        },
    }
