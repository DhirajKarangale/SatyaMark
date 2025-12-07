import base64
import numpy as np
import cv2
from PIL import Image
import io

from hf_image_inference import hf_infer
from hf_models import HF_MODELS


def load_image_bytes(image_path):
    with open(image_path, "rb") as f:
        return f.read()


def pil_from_bytes(b):
    return Image.open(io.BytesIO(b)).convert("RGB")


def safe_score(x):
    try:
        return float(max(0.0, min(1.0, float(x))))
    except:
        return 0.0


# -----------------------------------------------------------
# 1. Anatomy Validity — YOLO Pose Keypoint Count
# -----------------------------------------------------------
def estimate_anatomy_validity(image_bytes):
    out = hf_infer(HF_MODELS["yolo_pose"], image_bytes)
    if "predictions" not in out:
        return 0.5

    preds = out["predictions"]
    if not preds:
        return 0.5

    # count how many detections include keypoints
    kp_count = sum(1 for p in preds if "keypoints" in p)
    score = kp_count / 3
    return safe_score(score)


# -----------------------------------------------------------
# 2. Physics Correctness — YOLO Detection Confidence
# -----------------------------------------------------------
def estimate_physics_correctness(image_bytes):
    out = hf_infer(HF_MODELS["yolo_detect"], image_bytes)
    if "predictions" not in out:
        return 0.5

    preds = out["predictions"]
    if not preds:
        return 0.5

    confs = [p.get("score", 0.5) for p in preds]
    return safe_score(float(np.mean(confs)))


# -----------------------------------------------------------
# 3. Depth + Perspective — Depth Anything
# -----------------------------------------------------------
def estimate_depth_and_perspective(image_bytes):
    out = hf_infer(HF_MODELS["depth"], image_bytes)
    if "depth_map" not in out:
        return 0.5, None

    try:
        depth_img = Image.open(io.BytesIO(base64.b64decode(out["depth_map"])))
        depth_np = np.array(depth_img).astype(np.float32)

        depth_norm = (depth_np - depth_np.min()) / (
            depth_np.max() - depth_np.min() + 1e-6
        )

        var = np.var(depth_norm)
        score = safe_score(1 - var)

        return score, depth_norm
    except:
        return 0.5, None


# -----------------------------------------------------------
# 4. Lighting Consistency — gradient direction uniformity
# -----------------------------------------------------------
def estimate_lighting_consistency(image_bytes):
    pil_img = pil_from_bytes(image_bytes)
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0

    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(img, cv2.CV_32F, 0, 1)

    ang = np.arctan2(gy, gx).flatten()
    mag = np.sqrt(gx * gx + gy * gy).flatten()

    if mag.sum() == 0:
        return 0.5

    hist, _ = np.histogram(ang, bins=36, weights=mag)
    dominant = hist.max() / (hist.sum() + 1e-6)

    return safe_score(0.4 + 0.6 * dominant)


# -----------------------------------------------------------
# 5. Reflection Correctness — specular highlight + smoothness
# -----------------------------------------------------------
def estimate_reflection_correctness(image_bytes):
    pil_img = pil_from_bytes(image_bytes)
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0

    lap = cv2.Laplacian(img, cv2.CV_32F)
    local_var = cv2.blur(lap * lap, (15, 15))
    bright = (img > 0.85).astype(np.uint8)

    mask = ((local_var > 0.0005) & (bright == 1)).astype(np.uint8)

    area = mask.sum() / img.size

    # small reflection → high correctness
    score = safe_score(1 - min(area * 5, 1.0))
    return score


# -----------------------------------------------------------
# 6. Material Realism — CLIP Embedding Strength
# -----------------------------------------------------------
def estimate_material_realism(image_bytes):
    out = hf_infer(HF_MODELS["clip"], image_bytes)
    if "clip_embeddings" not in out:
        return 0.5

    emb = np.array(out["clip_embeddings"])
    mag = np.linalg.norm(emb)
    return safe_score(min(1.0, mag / 50))


# -----------------------------------------------------------
# 7. Object Logic — ViT Classification Probability
# -----------------------------------------------------------
def estimate_object_logic(image_bytes):
    out = hf_infer(HF_MODELS["vit"], image_bytes)

    if "labels" not in out:
        return 0.5

    scores = [l["score"] for l in out["labels"]]
    return safe_score(max(scores) if scores else 0.5)


# -----------------------------------------------------------
# FINAL PIPELINE — MATCHES YOUR EXACT OUTPUT FORMAT
# -----------------------------------------------------------
def semantic_consistency_analyze(image_path):

    img_bytes = load_image_bytes(image_path)

    anatomy = estimate_anatomy_validity(img_bytes)
    physics = estimate_physics_correctness(img_bytes)
    depth_score, depth_map = estimate_depth_and_perspective(img_bytes)
    lighting = estimate_lighting_consistency(img_bytes)
    reflection = estimate_reflection_correctness(img_bytes)
    material = estimate_material_realism(img_bytes)
    logic = estimate_object_logic(img_bytes)

    weights = {
        "anatomy_validity": 0.12,
        "physics_correctness": 0.18,
        "lighting_consistency": 0.20,
        "reflection_correctness": 0.10,
        "depth_and_perspective": 0.20,
        "material_realism": 0.10,
        "object_logic": 0.10,
    }

    vals = {
        "anatomy_validity": anatomy,
        "physics_correctness": physics,
        "lighting_consistency": lighting,
        "reflection_correctness": reflection,
        "depth_and_perspective": depth_score,
        "material_realism": material,
        "object_logic": logic,
    }

    overall = sum(vals[k] * weights[k] for k in vals)

    return {
        "semantic_consistency": {
            "status": "ok",
            "consistency_score": safe_score(overall),
            "details": {k: safe_score(vals[k]) for k in vals},
            "notes": "",
        }
    }
