# inference/dino.py
"""
DINOv2 embedding extraction + SVM scoring pipeline.

get_dino_embedding(image) -> 1D numpy embedding (1024)
score_with_svm(embedding) -> probability [0,1]

SVM is expected to be trained separately and saved to models/saved_models/dino_svm.joblib
"""
import os
import numpy as np
import torch
from joblib import load
from models.model_wrappers import get_dino_model
from inference.utils import open_image, to_numpy
from torchvision import transforms

SVM_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "saved_models", "dino_svm.joblib")

def get_dino_embedding(image, device=None):
    proc, model, device = get_dino_model(device)
    img = open_image(image)
    # Use processor if available else basic transforms
    if hasattr(proc, "images_processor") or hasattr(proc, "transform"): 
        # Many HF processors accept PIL images as list
        inputs = proc(images=img, return_tensors="pt")
    else:
        # fallback transform
        tf = transforms.Compose([
            transforms.Resize((224,224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=(0.5,0.5,0.5), std=(0.5,0.5,0.5))
        ])
        t = tf(img).unsqueeze(0)
        inputs = {"pixel_values": t}
    inputs = {k: v.to(device) for k,v in inputs.items()}
    with torch.no_grad():
        out = model(**inputs)
        # get last_hidden_state or pooled output depending on model
        if hasattr(out, "last_hidden_state"):
            emb = out.last_hidden_state[:,0,:].detach().cpu().numpy().squeeze()
        elif hasattr(out, "pooler_output"):
            emb = out.pooler_output.detach().cpu().numpy().squeeze()
        else:
            # fallback to mean pooling
            emb = out.logits.detach().cpu().numpy().mean(axis=0)
    return emb.astype(np.float32)

def score_with_svm(embedding):
    if not os.path.exists(SVM_PATH):
        raise FileNotFoundError(f"DINO SVM model not found at {SVM_PATH}. Train it using fusion/train_fusion.py")
    svm = load(SVM_PATH)
    prob = svm.predict_proba(embedding.reshape(1,-1))[0,1]
    return float(prob)
