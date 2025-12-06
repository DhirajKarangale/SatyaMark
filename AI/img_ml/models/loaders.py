# models/loaders.py
"""
Model loader utilities for Hugging Face models with caching and device management.
Exposes simple functions to get model + preprocessor.
"""
import os
from functools import lru_cache
from pathlib import Path
import torch
from transformers import AutoProcessor, AutoModel, AutoModelForImageClassification, AutoFeatureExtractor, CLIPProcessor, CLIPModel

CACHE_DIR = os.getenv("HF_HOME", None) or os.path.join(os.path.expanduser("~"), ".cache", "huggingface")

def get_device(prefer_cuda=True):
    if prefer_cuda and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")

@lru_cache(maxsize=8)
def load_processor(model_name: str):
    return AutoProcessor.from_pretrained(model_name, cache_dir=CACHE_DIR)

@lru_cache(maxsize=8)
def load_feature_extractor(model_name: str):
    return AutoFeatureExtractor.from_pretrained(model_name, cache_dir=CACHE_DIR)

@lru_cache(maxsize=8)
def load_image_model(model_name: str, device=None, use_auto=True):
    device = device or get_device()
    if use_auto:
        model = AutoModel.from_pretrained(model_name, cache_dir=CACHE_DIR)
    else:
        model = AutoModelForImageClassification.from_pretrained(model_name, cache_dir=CACHE_DIR)
    model.to(device)
    model.eval()
    return model

@lru_cache(maxsize=4)
def load_clip(model_name: str, device=None):
    device = device or get_device()
    model = CLIPModel.from_pretrained(model_name, cache_dir=CACHE_DIR)
    model.to(device)
    model.eval()
    return model
