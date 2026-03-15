import imghdr
import requests
import numpy as np
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image

MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/tiff"}
ALLOWED_FORMATS = {"jpeg", "png", "webp", "tiff"}


def validate_url(url):
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Invalid URL scheme")

    if not parsed.netloc:
        raise ValueError("Invalid URL")

def download_image(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
    }

    response = requests.get(url, headers=headers, timeout=15)

    if response.status_code != 200:
        raise ValueError(f"HTTP error: {response.status_code}")

    content_type = response.headers.get("Content-Type", "").split(";")[0]

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"Unsupported content type: {content_type}")

    image_bytes = response.content

    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError("Image too large")

    return image_bytes

def validate_image_bytes(image_bytes):
    image_type = imghdr.what(None, h=image_bytes)

    if image_type not in ALLOWED_FORMATS:
        raise ValueError(f"Invalid image format: {image_type}")

    image = Image.open(BytesIO(image_bytes))
    image.verify()

    image = Image.open(BytesIO(image_bytes))

    return image, image_type


def prepare_pipeline_image(image, image_bytes, image_type):
    rgb_image = image.convert("RGB")
    gray_np = np.array(rgb_image.convert("L"), dtype=np.float32)

    return {
        "pixels_gray": gray_np,
        "pil_image": rgb_image,
        "bytes": image_bytes,
        "format": image_type,
        "width": rgb_image.size[0],
        "height": rgb_image.size[1],
        "exif": image.getexif(),
    }


def process(url):
    validate_url(url)

    image_bytes = download_image(url)

    image, image_type = validate_image_bytes(image_bytes)

    result = prepare_pipeline_image(image, image_bytes, image_type)
        
    return result