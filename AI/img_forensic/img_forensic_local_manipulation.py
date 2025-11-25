import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance


def ela_analysis(img_np):
    """Compute Error Level Analysis map on a NumPy (cv2) image."""
    im = Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB))

    im.save("ela_temp.jpg", "JPEG", quality=95)
    ela = ImageChops.difference(im, Image.open("ela_temp.jpg"))
    ela = ImageEnhance.Brightness(ela).enhance(20)
    ela_np = np.array(ela)
    return ela_np


def noise_residual(img):
    blur = cv2.GaussianBlur(img, (9, 9), 0)
    residual = cv2.absdiff(img, blur)
    gray = cv2.cvtColor(residual, cv2.COLOR_BGR2GRAY)
    return gray


def texture_discontinuity(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    return float(abs(lap).mean())


def shadow_inconsistency(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sob = cv2.Sobel(gray, cv2.CV_64F, 1, 1)
    return float(sob.std())


def reflection_inconsistency(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return float(hsv[..., 2].std())


def region_count_from_ela(ela_map):
    gray = cv2.cvtColor(ela_map, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
    return int((thresh > 0).sum())


def local_manipulation_analyze(image_path):
    img_np = cv2.imread(image_path, cv2.IMREAD_COLOR)
    try:
        if img_np is None:
            raise Exception("Invalid or empty image")

        ela_map = ela_analysis(img_np)

        noise_map = noise_residual(img_np)

        region_count = region_count_from_ela(ela_map)

        shadow = shadow_inconsistency(img_np)
        reflection = reflection_inconsistency(img_np)
        texture = texture_discontinuity(img_np)

        confidence = round(
            min(
                1.0,
                (
                    shadow / 100
                    + reflection / 150
                    + texture / 50
                    + region_count / 100000
                ),
            ),
            4,
        )

        manipulated = confidence > 0.35 or region_count > 5000

        result = {
            "local_manipulation": {
                "status": "ok",
                "manipulated_regions_detected": bool(manipulated),
                "confidence": confidence,
                "details": {
                    "region_count": int(region_count),
                    "manipulation_heatmap": None,
                    "shadow_inconsistency": round(shadow, 4),
                    "reflection_inconsistency": round(reflection, 4),
                    "texture_discontinuity": round(texture, 4),
                },
                "notes": "",
            }
        }
        return result

    except Exception as e:
        return {
            "local_manipulation": {
                "status": "error",
                "manipulated_regions_detected": False,
                "confidence": 0.0,
                "details": {},
                "notes": str(e),
            }
        }
