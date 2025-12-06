# fusion/meta_model.py
"""
Meta model helper: can create pipeline for logistic regression / lightgbm / mlp.
"""
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
import joblib
import os

def create_meta_model(method="logistic", **kwargs):
    method = method.lower()
    if method == "logistic":
        clf = LogisticRegression(solver="lbfgs", max_iter=2000)
    elif method == "mlp":
        clf = MLPClassifier(hidden_layer_sizes=(32,16), max_iter=1000)
    else:
        # try lightgbm if installed
        try:
            import lightgbm as lgb
            if method == "lgbm":
                clf = lgb.LGBMClassifier(n_estimators=200)
            else:
                raise ValueError("Unknown method")
        except Exception:
            clf = LogisticRegression(solver="lbfgs", max_iter=2000)
    return clf

def save_model(model, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
