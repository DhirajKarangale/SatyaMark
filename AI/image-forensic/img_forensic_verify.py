import os
import imghdr
import requests
import tempfile
from PIL import Image
from urllib.parse import urlparse

from img_forensic_watermark_signature import watermark_analyze
from img_forensic_sensor_fingerprint import sensor_fingerprint_analyze
from img_forensic_gan_artifacts import gan_artifacts_analyze
from img_forensic_gan_artifacts_ml import gan_artifacts_ml_analyze
from img_forensic_local_manipulation import local_manipulation_analyze
from img_forensic_metadata import metadata_analysis
from img_forensic_semantic_consistency import (
    semantic_consistency_analyze,
)
from img_forensic_forensic_decision import classify_image


def verify_img_forensic(image_path: str):
    """Run full forensic pipeline on local image path"""
    try:
        w = watermark_analyze(image_path)
        s = sensor_fingerprint_analyze(image_path)
        g = gan_artifacts_analyze(image_path)
        gml = gan_artifacts_ml_analyze(image_path)
        l = local_manipulation_analyze(image_path)
        m = metadata_analysis(image_path)
        sc = semantic_consistency_analyze(image_path)

        return classify_image(w, s, g, l, m, sc)

    except Exception as e:
        return {"error": str(e)}


def verify_img_forensic_url(url: str, timeout: int = 10, max_bytes: int = 5 * 1024 * 1024):
    """Validate URL, download image safely, run analysis"""
    try:
        p = urlparse(url)
        if p.scheme not in ("http", "https") or not p.netloc:
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

        return verify_img_forensic(temp_path)

    except Exception as e:
        return {"error": str(e)}

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


def evaluate_img_forensic(ai_folder: str, real_folder: str):
    """Evaluate AI and NON-AI datasets and return stats"""

    def evaluate_folder(path, expected):
        total, correct = 0, 0
        for file in os.listdir(path):
            if not file.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue

            img_path = os.path.join(path, file)
            total += 1

            result = verify_img_forensic(img_path)
            predicted = result.get("mark", "").upper()

            if predicted == expected.upper():
                correct += 1

        incorrect = total - correct
        accuracy = (correct / total * 100) if total else 0

        return {
            "total": total,
            "correct": correct,
            "incorrect": incorrect,
            "accuracy": accuracy,
        }

    ai_stats = evaluate_folder(ai_folder, "AI")
    real_stats = evaluate_folder(real_folder, "NONAI")

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
