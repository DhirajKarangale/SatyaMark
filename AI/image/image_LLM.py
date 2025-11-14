import torch
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import joblib
import cv2
import os
from PIL import ImageChops
import piexif


# ================================================================
# 1. Load CLIP backbone (Stable + Official Transformers Model)
# ================================================================
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model.eval()


# ================================================================
# 2. Load the pretrained AI detector (Logistic Regression)
# ================================================================
# I will provide this file: ai_detector_lr_model.pkl
clf = joblib.load("ai_detector_lr_model.pkl")   # <-- make sure this file exists


# ================================================================
# 3. CLIP Embedding Extractor
# ================================================================
def get_embedding(image_path):
    img = Image.open(image_path).convert("RGB")
    inputs = clip_processor(images=img, return_tensors="pt")

    with torch.no_grad():
        emb = clip_model.get_image_features(**inputs)

    emb = emb.cpu().numpy().flatten()
    return emb


# ================================================================
# 4. FFT Score (Image Frequency Signature)
# ================================================================
def fft_score(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (512, 512))
    f = np.fft.fft2(img)
    magnitude = 20 * np.log(np.abs(f) + 1e-8)
    score = float(np.std(magnitude)) / 100
    return max(0, min(score, 1))


# ================================================================
# 5. ELA Score
# ================================================================
def ela_score(image_path, quality=90):
    img = Image.open(image_path).convert("RGB")
    temp_path = "_temp_resave.jpg"
    img.save(temp_path, "JPEG", quality=quality)
    resaved = Image.open(temp_path)

    diff = ImageChops.difference(img, resaved)
    arr = np.array(diff.convert("L"))
    score = np.mean(arr) / 255

    os.remove(temp_path)
    return float(score)


# ================================================================
# 6. Metadata Score
# ================================================================
def metadata_score(image_path):
    try:
        exif = piexif.load(image_path)
        has_exif = bool(exif.get("0th") or exif.get("Exif"))
    except:
        has_exif = False
    return 0.2 if not has_exif else 0.0


# ================================================================
# 7. Final Ensemble Detection
# ================================================================
def detect_ai(image_path):
    # 1. CLIP Embedding → Logistic Regression
    emb = get_embedding(image_path)
    prob_ai_clip = clf.predict_proba([emb])[0][1]

    # 2–4 Additional forensic signals
    fft_ai = 1 - fft_score(image_path)
    ela_ai = ela_score(image_path)
    meta_ai = metadata_score(image_path)

    # Weighted ensemble
    final_ai_score = (
        prob_ai_clip * 0.70 +
        fft_ai * 0.15 +
        ela_ai * 0.10 +
        meta_ai * 0.05
    )

    final_ai_score = max(0, min(final_ai_score, 1))

    mark = "AI" if final_ai_score >= 0.5 else "NON AI"
    accuracy = round(final_ai_score * 100, 2)

    return {
        "mark": mark,
        "accuracy": accuracy,
        "breakdown": {
            "CLIP_AI": prob_ai_clip,
            "FFT": fft_ai,
            "ELA": ela_ai,
            "Metadata": meta_ai
        }
    }


# ================================================================
# MAIN (Test)
# ================================================================
if __name__ == "__main__":
    img = "JJ3D.png"
    print(detect_ai(img))
