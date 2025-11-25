# models/model_wrappers.py
"""
Higher-level wrappers for the specific models used by SatyaMark.
Wraps DINOv2, FatFormer, GhostNet, MantraNet, CLIP H/14 and bigG.
Each function returns model objects and processors ready for inference.
"""
from .loaders import load_processor, load_image_model, load_clip, get_device

# Exact HF model ids from requirements
MODEL_IDS = {
    "dino": "facebook/dinov2-large",
    "fatformer": "yuchuantian/AIGC_detector_zhv2",
    "ghostnet": "buildborderless/CommunityForensics-DeepfakeDet-ViT",
    "mantranet": "nvidia/segformer-b0-finetuned-ade-512-512",
    "clip_h14": "openai/clip-vit-large-patch14",
    "clip_bigg": "openai/clip-vit-base-patch32",
}


def get_dino_model(device=None):
    device = device or get_device()
    proc = load_processor(MODEL_IDS["dino"])
    model = load_image_model(MODEL_IDS["dino"], device=device, use_auto=True)
    return proc, model, device


def get_fatformer_model(device=None):
    """
    Defensive loader: try to load FatFormer if MODEL_IDS provides an ID,
    otherwise return (None, None, device). This prevents accidental HF download retries.
    """
    model_id = MODEL_IDS.get("fatformer", None)
    if not model_id:
        return None, None, get_device()

    try:
        import torch
        from transformers import AutoImageProcessor, AutoModelForImageClassification

        if device is None:
            device = get_device()
        processor = AutoImageProcessor.from_pretrained(model_id)
        model = AutoModelForImageClassification.from_pretrained(model_id).to(device)
        model.eval()
        return processor, model, device
    except Exception as e:
        # Log and fallback to None — calling code should handle None
        print(f"[model_wrappers] Unable to load FatFormer ({model_id}): {e}")
        return None, None, get_device()


def get_ghostnet_model(device=None):
    device = device or get_device()
    proc = load_processor(MODEL_IDS["ghostnet"])
    model = load_image_model(MODEL_IDS["ghostnet"], device=device, use_auto=True)
    return proc, model, device


def get_mantranet_model(device=None):
    device = device or get_device()
    proc = load_processor(MODEL_IDS["mantranet"])
    model = load_image_model(MODEL_IDS["mantranet"], device=device, use_auto=True)
    return proc, model, device


def get_clip_model_h14(device=None):
    device = device or get_device()
    proc = load_processor(MODEL_IDS["clip_h14"])
    model = load_clip(MODEL_IDS["clip_h14"], device=device)
    return proc, model, device


def get_clip_model_bigg(device=None):
    device = device or get_device()
    proc = load_processor(MODEL_IDS["clip_bigg"])
    model = load_clip(MODEL_IDS["clip_bigg"], device=device)
    return proc, model, device
