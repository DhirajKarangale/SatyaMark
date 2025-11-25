# inference/clip_models.py
import numpy as np
import torch
from AI.img_ml.models.model_wrappers import get_clip_model_h14, get_clip_model_bigg
from AI.img_ml.inference.utils import open_image, to_numpy

# We'll compute image embeddings and then load small classifier mapping embeddings -> AI probability
# Classifiers expected: models/saved_models/clip_h14_clf.joblib, clip_bigg_clf.joblib

import os
from joblib import load

CLIP_H14_CLF = os.path.join(os.path.dirname(__file__), "..", "models", "saved_models", "clip_h14_clf.joblib")
CLIP_BIGG_CLF = os.path.join(os.path.dirname(__file__), "..", "models", "saved_models", "clip_bigg_clf.joblib")

def get_clip_embedding(proc, model, image, device=None):
    device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    img = open_image(image)
    inputs = proc(images=img, return_tensors="pt")
    inputs = {k: v.to(device) for k,v in inputs.items()}
    with torch.no_grad():
        out = model.get_image_features(**inputs)
        emb = out.cpu().numpy().reshape(-1)
        # normalize
        emb = emb / (np.linalg.norm(emb) + 1e-12)
        return emb.astype(np.float32)

def clip_h14_prob(image, device=None):
    proc, model, device = get_clip_model_h14(device)
    emb = get_clip_embedding(proc, model, image, device)
    if not os.path.exists(CLIP_H14_CLF):
    # classifier not trained yet — return neutral score
        return 0.5
    clf = load(CLIP_H14_CLF)
    prob = clf.predict_proba(emb.reshape(1,-1))[0,1]
    return float(prob)

def clip_bigg_prob(image, device=None):
    proc, model, device = get_clip_model_bigg(device)
    emb = get_clip_embedding(proc, model, image, device)
    if not os.path.exists(CLIP_BIGG_CLF):
        raise FileNotFoundError(f"Clip bigG classifier not found at {CLIP_BIGG_CLF}")
    clf = load(CLIP_BIGG_CLF)
    prob = clf.predict_proba(emb.reshape(1,-1))[0,1]
    return float(prob)
