# inference/ghostnet.py
import torch
from AI.img_ml.models.model_wrappers import get_ghostnet_model
from AI.img_ml.inference.utils import open_image
import numpy as np

def get_ghostnet_prob(image, device=None):
    proc, model, device = get_ghostnet_model(device)
    img = open_image(image)
    inputs = proc(images=img, return_tensors="pt")
    inputs = {k: v.to(device) for k,v in inputs.items()}
    with torch.no_grad():
        out = model(**inputs)
        logits = getattr(out, "logits", None)
        if logits is None:
            if "logits" in out:
                logits = out["logits"]
        if logits is None:
            raise RuntimeError("Unexpected ghostnet output.")
        probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
        # assume index 1 -> fake/manipulated
        return float(probs[1])
