import torch
import numpy as np
from PIL import Image, ImageChops
from transformers import CLIPProcessor, CLIPModel
import joblib
import cv2
import piexif
import os


# ========================================================
# 1. Load CLIP model (Transformers-compatible)
# ========================================================
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model.eval()


# ========================================================
# 2. Load your trained detector
# ========================================================
model_data = joblib.load("ai_detector_lr_model.pkl")
scaler = model_data["scaler"]
clf = model_data["clf"]


# ========================================================
# 3. Extract CLIP embedding
# ========================================================
def get_embedding(image_path):
    img = Image.open(image_path).convert("RGB")
    inputs = clip_processor(images=img, return_tensors="pt")

    with torch.no_grad():
        emb = clip_model.get_image_features(**inputs)

    return emb.cpu().numpy().flatten()


# ========================================================
# 4. FFT Score
# ========================================================
def fft_score(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (512, 512))
    f = np.fft.fft2(img)
    magnitude = 20 * np.log(np.abs(f) + 1e-8)
    score = float(np.std(magnitude)) / 100
    return max(0, min(score, 1))


# ========================================================
# 5. ELA Score
# ========================================================
def ela_score(image_path, quality=90):
    img = Image.open(image_path).convert("RGB")
    temp = "_temp.jpg"
    img.save(temp, "JPEG", quality=quality)
    resaved = Image.open(temp)

    diff = ImageChops.difference(img, resaved)
    arr = np.array(diff.convert("L"))
    os.remove(temp)

    return float(np.mean(arr) / 255)


# ========================================================
# 6. Metadata Score
# ========================================================
def metadata_score(image_path):
    try:
        exif = piexif.load(image_path)
        has_exif = bool(exif.get("0th") or exif.get("Exif"))
    except:
        has_exif = False
    return 0.2 if not has_exif else 0.0


# ========================================================
# 7. Final Ensemble Scoring
# ========================================================
def detect_ai(image_path):
    # CLIP embedding
    emb = get_embedding(image_path)
    emb_s = scaler.transform([emb])
    prob_ai_clip = clf.predict_proba(emb_s)[0][1]

    # Forensics components
    fft_ai = 1 - fft_score(image_path)
    ela_ai = ela_score(image_path)
    meta_ai = metadata_score(image_path)

    # Weighted fusion
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
            "Metadata": meta_ai,
        }
    }


# ========================================================
# RUN TEST
# ========================================================
if __name__ == "__main__":
    test_img = "Logo.JPG"  # set the correct path
    print(detect_ai(test_img))
