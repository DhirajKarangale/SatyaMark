# utils/persistence.py
import joblib, os
def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def save_joblib(obj, path):
    ensure_dir(path)
    joblib.dump(obj, path)

def load_joblib(path):
    return joblib.load(path)
