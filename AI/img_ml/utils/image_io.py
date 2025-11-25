# utils/image_io.py
from PIL import Image
import os

def load_image(path):
    return Image.open(path).convert("RGB")

def save_image(img, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
# utils/image_io.py
from PIL import Image
import os

def load_image(path):
    return Image.open(path).convert("RGB")

def save_image(img, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
