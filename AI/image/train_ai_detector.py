"""
Train a logistic-regression AI vs REAL detector using CLIP embeddings.

Usage:
    python train_ai_detector.py --ai_dir data/ai --real_dir data/real --out ai_detector_lr_model.pkl

Outputs:
    - ai_detector_lr_model.pkl (joblib, contains sklearn pipeline: StandardScaler -> LogisticRegression -> CalibratedClassifierCV)
    - metrics printed to console and a small CSV with embeddings optionally.
"""

from pathlib import Path
from PIL import Image
import numpy as np
import joblib

import torch
from transformers import CLIPProcessor, CLIPModel

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, classification_report


def list_images(folder, exts=(".jpg", ".jpeg", ".png", ".webp")):
    p = Path(folder)
    return [str(x) for x in p.rglob("*") if x.suffix.lower() in exts]


def extract_clip_embeddings(image_paths, device="cpu", batch_size=8):
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    model.eval()
    model.to(device)

    embeddings = []
    for i in range(0, len(image_paths), batch_size):
        batch_paths = image_paths[i : i + batch_size]
        imgs = []
        for p in batch_paths:
            try:
                img = Image.open(p).convert("RGB")
                imgs.append(img)
            except Exception as e:
                imgs.append(Image.new("RGB", (224, 224), (128, 128, 128)))
        inputs = processor(images=imgs, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            emb = model.get_image_features(**inputs)
            emb = emb.cpu().numpy()
        embeddings.append(emb)
    if embeddings:
        return np.vstack(embeddings)
    else:
        return np.zeros((0, 512), dtype=np.float32)


def build_dataset(ai_dir, real_dir, ai_limit=None, real_limit=None, shuffle=True):
    ai_paths = list_images(ai_dir)
    real_paths = list_images(real_dir)
    if ai_limit:
        ai_paths = ai_paths[:ai_limit]
    if real_limit:
        real_paths = real_paths[:real_limit]
    paths = ai_paths + real_paths
    labels = [1] * len(ai_paths) + [0] * len(real_paths)
    if shuffle:
        rng = np.random.default_rng(42)
        perm = rng.permutation(len(paths))
        paths = [paths[i] for i in perm]
        labels = [labels[i] for i in perm]
    return paths, np.array(labels, dtype=np.int64)


def main(args):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Device:", device)

    paths, labels = build_dataset(
        args.ai_dir, args.real_dir, ai_limit=args.ai_limit, real_limit=args.real_limit
    )
    print(
        f"Found {len(paths)} images: {labels.sum()} AI, {len(labels)-labels.sum()} REAL"
    )

    # split
    train_paths, val_paths, y_train, y_val = train_test_split(
        paths, labels, test_size=0.15, random_state=42, stratify=labels
    )
    print(f"Train size: {len(train_paths)}, Val size: {len(val_paths)}")

    # Extract embeddings
    print("Extracting train embeddings...")
    X_train = extract_clip_embeddings(
        train_paths, device=device, batch_size=args.batch_size
    )
    print("Extracting val embeddings...")
    X_val = extract_clip_embeddings(
        val_paths, device=device, batch_size=args.batch_size
    )

    # Standardize
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)

    # Classifier: LogisticRegression + calibration
    print("Training logistic regression...")
    base_clf = LogisticRegression(C=1.0, max_iter=1000, solver="lbfgs")
    clf_cal = CalibratedClassifierCV(
        base_clf, cv=3, method="isotonic"
    )  # isotonic for better probs
    clf_cal.fit(X_train_s, y_train)

    # Eval
    probs = clf_cal.predict_proba(X_val_s)[:, 1]
    preds = (probs >= 0.5).astype(int)
    auc = roc_auc_score(y_val, probs)
    acc = accuracy_score(y_val, preds)
    print("Validation AUC: %.4f  Acc: %.4f" % (auc, acc))
    print(classification_report(y_val, preds, digits=4))

    # Save pipeline as dict
    out = {"scaler": scaler, "clf": clf_cal}
    joblib.dump(out, args.out, compress=3)
    print("Saved model to", args.out)

    # Optional: Save small metadata file
    with open(args.out + ".meta.txt", "w") as f:
        f.write(
            f"AUTO TRAINED MODEL\nAUC={auc:.4f}\nACC={acc:.4f}\nSamples={len(paths)}\n"
        )


if __name__ == "__main__":
    args = type("Args", (), {})()
    args.ai_dir = "./data/ai"
    args.real_dir = "./data/real"
    args.out = "ai_detector_lr_model.pkl"
    args.batch_size = 16
    args.ai_limit = None
    args.real_limit = None

    main(args)

