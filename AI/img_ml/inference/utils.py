# inference/utils.py
import torch
import numpy as np
from PIL import Image
import io

def open_image(path_or_bytes):
    if isinstance(path_or_bytes, (bytes, bytearray)):
        return Image.open(io.BytesIO(path_or_bytes)).convert("RGB")
    return Image.open(path_or_bytes).convert("RGB")

def to_numpy(tensor):
    if isinstance(tensor, torch.Tensor):
        return tensor.detach().cpu().numpy()
    return np.array(tensor)

def sigmoid(x):
    import math
    return 1.0 / (1.0 + math.exp(-x))
