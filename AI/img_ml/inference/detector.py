# inference/detector.py
"""
Main detection entrypoint: detect_ai_image(image_path)

Outputs:
{
  "mark": "AI" or "REAL",
  "confidence": 0-100,
  "breakdown": {
      "dino_prob": 0-1,
      "fatformer_prob": 0-1,
      "ghostnet_prob": 0-1,
      "clip_h14_prob": 0-1,
      "clip_bigg_prob": 0-1,
      "mantra_anomaly": 0-1,
      "forensic_score": 0-1
  },
  "heatmap_preview": "<path/to/heatmap.png or base64>"
}
"""

import os
import numpy as np
import joblib
from PIL import Image
import base64

from .dino import get_dino_embedding
from .fatformer import get_fatformer_prob
from .ghostnet import get_ghostnet_prob
from .mantranet import get_mantranet_heatmap, reduce_heatmap_to_score
from .clip_models import clip_h14_prob, clip_bigg_prob
from forensics.forensic_features import compute_forensic_features
from models.model_wrappers import get_device

# ----------------------------------------------
# MODEL PATHS
# ----------------------------------------------
AI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_DIR = os.path.join(AI_DIR, "..", "models", "saved_models")

META_MODEL_PATH = os.path.join(MODEL_DIR, "fusion_model.joblib")
SVM_PATH = os.path.join(MODEL_DIR, "dino_svm.joblib")

# ----------------------------------------------
# LOADERS (lazy loading)
# ----------------------------------------------
_meta_model = None
_dino_svm = None


def _load_meta_model():
    global _meta_model
    if _meta_model is None:
        if not os.path.exists(META_MODEL_PATH):
            raise FileNotFoundError(
                f"Fusion model not found at: {META_MODEL_PATH}. Train using fusion/train_fusion.py"
            )
        _meta_model = joblib.load(META_MODEL_PATH)
    return _meta_model


def _load_dino_svm():
    global _dino_svm
    if _dino_svm is None:
        if not os.path.exists(SVM_PATH):
            raise FileNotFoundError(
                f"DINO SVM not found at: {SVM_PATH}. Train it first."
            )
        _dino_svm = joblib.load(SVM_PATH)
    return _dino_svm


# ----------------------------------------------
# Optional: Save a heatmap preview
# ----------------------------------------------
def _save_heatmap_preview(heatmap_np):
    out_path = os.path.join(AI_DIR, "img_ml", "last_heatmap.jpg")

    hm = (255 * (heatmap_np - heatmap_np.min()) /
          (heatmap_np.max() - heatmap_np.min() + 1e-9)).astype("uint8")

    img = Image.fromarray(hm).convert("L").resize((512, 512))
    img.save(out_path)
    return out_path


# ----------------------------------------------
# MAIN DETECTION FUNCTION
# ----------------------------------------------
def detect_ai_image(image_path, device=None, return_heatmap_base64=False):
    device = device or get_device()

    breakdown = {}

    # -------------------------------
    # 1. DINO embedding + SVM score
    # -------------------------------
    try:
        emb = get_dino_embedding(image_path, device=device)
        svm = _load_dino_svm()
        dino_prob = float(svm.predict_proba(emb.reshape(1, -1))[0][1])
    except Exception:
        dino_prob = 0.5
    breakdown["dino_prob"] = dino_prob

    # -------------------------------
    # 2. FatFormer
    # -------------------------------
    try:
        fatformer_p = get_fatformer_prob(image_path, device=device)
    except Exception:
        fatformer_p = 0.5
    breakdown["fatformer_prob"] = float(fatformer_p)

    # -------------------------------
    # 3. GhostNet
    # -------------------------------
    try:
        ghost_p = get_ghostnet_prob(image_path, device=device)
    except Exception:
        ghost_p = 0.5
    breakdown["ghostnet_prob"] = float(ghost_p)

    # -------------------------------
    # 4. CLIP models
    # -------------------------------
    try:
        clip_h = clip_h14_prob(image_path, device=device)
    except Exception:
        clip_h = 0.5
    breakdown["clip_h14_prob"] = float(clip_h)

    try:
        clip_b = clip_bigg_prob(image_path, device=device)
    except Exception:
        clip_b = 0.5
    breakdown["clip_bigg_prob"] = float(clip_b)

    # -------------------------------
    # 5. MantraNet anomaly heatmap
    # -------------------------------
    try:
        heatmap = get_mantranet_heatmap(image_path, device=device)
        mantra_score = reduce_heatmap_to_score(heatmap)
        heatmap_path = _save_heatmap_preview(heatmap)
    except Exception:
        heatmap = None
        mantra_score = 0.0
        heatmap_path = None
    breakdown["mantra_anomaly"] = float(mantra_score)

    # -------------------------------
    # 6. Forensic features
    # -------------------------------
    try:
        forensic = compute_forensic_features(image_path)
        forensic_score = float(forensic.get("forensic_score", 0.0))
    except Exception:
        forensic_score = 0.0
    breakdown["forensic_score"] = forensic_score

    # ----------------------------------------
    # Assemble fusion feature vector
    # ----------------------------------------
    feature_vector = np.array([
        breakdown["dino_prob"],
        breakdown["fatformer_prob"],
        breakdown["ghostnet_prob"],
        breakdown["clip_h14_prob"],
        breakdown["clip_bigg_prob"],
        breakdown["mantra_anomaly"],
        breakdown["forensic_score"],
    ], dtype=np.float32).reshape(1, -1)

    # -------------------------------
    # 7. Fusion model final decision
    # -------------------------------
    try:
        meta = _load_meta_model()
        if hasattr(meta, "predict_proba"):
            final_score = float(meta.predict_proba(feature_vector)[0][1])
        else:
            final_score = float(meta.predict(feature_vector)[0])
            final_score = max(0.0, min(final_score, 1.0))
    except Exception:
        final_score = float(feature_vector.mean())

    mark = "AI" if final_score >= 0.5 else "REAL"
    confidence = final_score * 100.0

    # -------------------------------
    # Build final response
    # -------------------------------
    result = {
        "mark": mark,
        "confidence": confidence,
        "breakdown": breakdown,
        "heatmap_preview": None
    }

    if heatmap_path:
        if return_heatmap_base64:
            with open(heatmap_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            result["heatmap_preview"] = b64
        else:
            result["heatmap_preview"] = os.path.abspath(heatmap_path)

    return result
