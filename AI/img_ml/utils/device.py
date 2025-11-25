# utils/device.py
import torch
def get_device(prefer_gpu=True):
    if prefer_gpu and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")
