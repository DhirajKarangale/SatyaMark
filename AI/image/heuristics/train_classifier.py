import os
import sys
import glob
from pathlib import Path

# Add AI/image to sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from joblib import dump

from heuristics import feature_extractor
from heuristics import heuristic_verify
import downloader

def load_and_extract(img_dir):
    features = []
    files = glob.glob(os.path.join(img_dir, "*.*"))
    for f in files:
        try:
            img = downloader.process_local(f)
            data = heuristic_verify.run_heuristics(img)
            vec = feature_extractor.extract_feature_vector(data)
            features.append(vec)
        except Exception as e:
            print(f"Error processing {f}: {e}")
    return features

def augment_data(X, y, target_size=100, noise_level=0.01):
    if len(X) == 0:
        return np.array([]), np.array([])
    
    X = np.array(X)
    y = np.array(y)
    
    X_aug = []
    y_aug = []
    
    for i in range(target_size):
        idx = np.random.randint(0, len(X))
        sample = X[idx]
        noise = np.random.normal(0, noise_level, sample.shape)
        X_aug.append(sample + noise)
        y_aug.append(y[idx])
        
    return np.array(X_aug), np.array(y_aug)

def main():
    # Fix dataset path (2 levels up is AI/, then dataset/train)
    ai_dir = str(Path(__file__).resolve().parents[2] / "dataset" / "train" / "ai")
    real_dir = str(Path(__file__).resolve().parents[2] / "dataset" / "train" / "real")
    
    print(f"Loading AI images from {ai_dir}")
    X_ai = load_and_extract(ai_dir)
    y_ai = [1] * len(X_ai)
    
    print(f"Loading REAL images from {real_dir}")
    X_real = load_and_extract(real_dir)
    y_real = [0] * len(X_real)
    
    X = X_ai + X_real
    y = y_ai + y_real
    
    if not X:
        print("No training data found.")
        return
        
    # Feature augmentation to combat extreme small dataset (3 AI, 2 Real)
    X_train, y_train = augment_data(X, y, target_size=200, noise_level=0.05)
    
    clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    clf.fit(X_train, y_train)
    
    model_dir = os.path.join(str(Path(__file__).resolve().parent), "model")
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, "classifier.joblib")
    dump(clf, model_path)
    print(f"Model trained and saved to {model_path}")
    
    # Feature importances
    importances = clf.feature_importances_
    print("Feature Importances:", np.round(importances, 4))

if __name__ == "__main__":
    main()
