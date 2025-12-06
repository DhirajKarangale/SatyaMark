import torch
import numpy as np
from AI.img_ml.models.model_wrappers import get_mantranet_model
from AI.img_ml.inference.utils import open_image


def get_mantranet_heatmap(image, device=None):
    proc, model, device = get_mantranet_model(device)

    img = open_image(image)
    inputs = proc(images=img, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits  # shape: [1, num_labels, H, W]
        mask = logits.softmax(dim=1)
        # anomaly = "unclassified" label = last channel
        heatmap = mask[0, -1].detach().cpu().numpy()

    return heatmap


def reduce_heatmap_to_score(heatmap):
    # Simple anomaly heuristic:
    anomaly = float(np.mean(heatmap))
    return anomaly
