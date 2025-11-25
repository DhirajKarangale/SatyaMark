import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import os
import argparse
import pandas as pd
import numpy as np
from tqdm import tqdm
from joblib import dump
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score, accuracy_score
from fusion.meta_model import create_meta_model, save_model

from AI.img_ml.inference.dino import get_dino_embedding
from AI.img_ml.inference.ghostnet import get_ghostnet_prob
from AI.img_ml.inference.mantranet import get_mantranet_heatmap, reduce_heatmap_to_score
from AI.img_ml.inference.clip_models import clip_h14_prob, clip_bigg_prob
from AI.img_ml.inference.fatformer import get_fatformer_prob
from AI.img_ml.forensics.forensic_features import compute_forensic_features
from AI.img_ml.models.model_wrappers import get_device

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_CSV = os.path.join(ROOT_DIR, "dataset.csv")
SAVED_DIR = os.path.join(os.path.dirname(__file__), "..", "models", "saved_models")
METHOD = "logistic"


def extract_features_for_image(path, device=None):
    device = device or get_device()

    emb = get_dino_embedding(path, device=device)

    try:
        fat_p = get_fatformer_prob(path, device=device)
    except Exception:
        fat_p = 0.5

    try:
        ghost_p = get_ghostnet_prob(path, device=device)
    except Exception:
        ghost_p = 0.5

    try:
        heat = get_mantranet_heatmap(path, device=device)
        mantra = reduce_heatmap_to_score(heat)
    except Exception:
        mantra = 0.0

    forensic = compute_forensic_features(path)

    return {
        "dino_emb": emb,
        "fatformer_prob": fat_p,
        "ghostnet_prob": ghost_p,
        "mantra_anomaly": mantra,
        "forensic_score": forensic.get("forensic_score", 0.0),
    }


def main():
    df = pd.read_csv(DATASET_CSV)
    os.makedirs(SAVED_DIR, exist_ok=True)
    device = get_device()

    # -------------------------------
    # STAGE 1 — DINO SVM TRAINING
    # -------------------------------
    print("Extracting DINO embeddings...")
    embeddings = []
    labels = []

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        img_path = row["image_path"]

        if not os.path.exists(img_path):
            print("SKIP (missing file):", img_path)
            continue

        try:
            f = extract_features_for_image(img_path, device=device)
            emb = f["dino_emb"]
            embeddings.append(emb)
            labels.append(int(row["label"]))
        except Exception as e:
            print("SKIP (error):", img_path, e)

    if len(embeddings) == 0:
        raise RuntimeError("No DINO embeddings extracted. Stopping training.")

    X = np.vstack(embeddings)
    y = np.array(labels)

    print("Training DINO SVM...")
    svm = SVC(kernel="rbf", probability=False, class_weight="balanced")
    clf = CalibratedClassifierCV(svm, cv=3)
    clf.fit(X, y)
    dump(clf, os.path.join(SAVED_DIR, "dino_svm.joblib"))
    print("Saved DINO SVM.")

    # ---------------------------------
    # STAGE 2 — FUSION MODEL TRAINING
    # ---------------------------------
    print("Building fusion dataset...")
    Xf = []
    yf = []

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        img_path = row["image_path"]

        try:
            emb = get_dino_embedding(img_path, device=device)
            dino_prob = float(clf.predict_proba(emb.reshape(1, -1))[0][1])
        except Exception as e:
            print("SKIP fusion (dino->prob):", img_path, e)
            continue

        fat = 0.5  # fatformer disabled safely

        try:
            ghost = get_ghostnet_prob(img_path, device=device)
        except Exception:
            ghost = 0.5

        try:
            hm = get_mantranet_heatmap(img_path, device=device)
            mantra = reduce_heatmap_to_score(hm)
        except Exception:
            mantra = 0.0

        try:
            clip_h = clip_h14_prob(img_path, device=device)
        except Exception:
            clip_h = 0.5

        try:
            clip_b = clip_bigg_prob(img_path, device=device)
        except Exception:
            clip_b = 0.5

        try:
            ff = compute_forensic_features(img_path)
            forensic_score = ff.get("forensic_score", 0.0)
        except Exception:
            forensic_score = 0.0

        feat = [dino_prob, fat, ghost, clip_h, clip_b, mantra, forensic_score]
        Xf.append(feat)
        yf.append(int(row["label"]))

    if len(Xf) == 0:
        raise RuntimeError(
            "Fusion feature extraction produced 0 samples. Cannot train."
        )

    Xf = np.vstack(Xf)
    yf = np.array(yf)

    X_train, X_val, y_train, y_val = train_test_split(
        Xf, yf, test_size=0.2, random_state=42, stratify=yf
    )

    print("Training fusion model...")
    meta = create_meta_model(method=METHOD)
    meta.fit(X_train, y_train)

    y_pred = meta.predict(X_val)
    y_proba = meta.predict_proba(X_val)[:, 1]

    auc = roc_auc_score(y_val, y_proba)
    acc = accuracy_score(y_val, y_pred)

    print("Fusion AUC:", auc)
    print("Fusion ACC:", acc)

    save_model(meta, os.path.join(SAVED_DIR, "fusion_model.joblib"))
    print("Saved fusion model.")
    print("Training complete.")


if __name__ == "__main__":
    main()
