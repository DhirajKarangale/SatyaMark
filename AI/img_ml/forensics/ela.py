# forensics/ela.py
from PIL import Image, ImageChops, ImageEnhance
import io

def compute_ela_image(img_path_or_pil, quality=90):
    """
    Compute Error Level Analysis image as grayscale PIL image normalized to [0..255].
    """
    if isinstance(img_path_or_pil, Image.Image):
        img = img_path_or_pil
    else:
        img = Image.open(img_path_or_pil).convert("RGB")
    # save to bytes with reduced quality
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    recompressed = Image.open(buffer).convert("RGB")
    ela = ImageChops.difference(img, recompressed)
    # amplify differences
    extrema = ela.getextrema()
    max_diff = max([e[1] for e in extrema])
    scale = 255.0 / max(max_diff, 1)
    ela = ImageEnhance.Brightness(ela).enhance(scale)
    ela_gray = ela.convert("L")
    return ela_gray
