import json
import numpy as np
from PIL import Image


def fft_features(gray):

    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    magnitude = np.log(np.abs(fshift) + 1)

    h, w = magnitude.shape

    center = magnitude[h//2-10:h//2+10, w//2-10:w//2+10]
    outer = magnitude.copy()
    outer[h//2-10:h//2+10, w//2-10:w//2+10] = 0

    return {
        "center_energy": float(np.mean(center)),
        "outer_energy": float(np.mean(outer)),
        "energy_ratio": float(np.mean(center) / (np.mean(outer) + 1e-6))
    }


def noise_features(gray):

    blur = (
        gray[:-2, :-2] + gray[1:-1, :-2] + gray[2:, :-2] +
        gray[:-2, 1:-1] + gray[1:-1, 1:-1] + gray[2:, 1:-1] +
        gray[:-2, 2:] + gray[1:-1, 2:] + gray[2:, 2:]
    ) / 9

    residual = gray[1:-1, 1:-1] - blur

    return {
        "residual_variance": float(np.var(residual)),
        "residual_mean": float(np.mean(residual)),
        "residual_std": float(np.std(residual))
    }


def gradient_features(gray):

    gy, gx = np.gradient(gray)

    magnitude = np.sqrt(gx**2 + gy**2)

    return {
        "gradient_mean": float(np.mean(magnitude)),
        "gradient_variance": float(np.var(magnitude)),
        "gradient_std": float(np.std(magnitude))
    }


def edge_features(gray):

    gy, gx = np.gradient(gray)
    edges = np.sqrt(gx**2 + gy**2)

    threshold = np.mean(edges)

    edge_pixels = np.sum(edges > threshold)

    density = edge_pixels / edges.size

    return {
        "edge_density": float(density),
        "edge_mean": float(np.mean(edges)),
        "edge_variance": float(np.var(edges))
    }


def symmetry_features(gray):

    h, w = gray.shape

    left = gray[:, :w//2]
    right = np.fliplr(gray[:, w//2:])

    min_w = min(left.shape[1], right.shape[1])

    left = left[:, :min_w]
    right = right[:, :min_w]

    diff = np.abs(left - right)

    return {
        "symmetry_score": float(1 - np.mean(diff) / 255),
        "symmetry_variance": float(np.var(diff)),
        "symmetry_mean_diff": float(np.mean(diff))
    }


def texture_block_features(gray):

    block_size = 32

    h, w = gray.shape

    block_vars = []

    for y in range(0, h - block_size, block_size):
        for x in range(0, w - block_size, block_size):

            block = gray[y:y+block_size, x:x+block_size]

            block_vars.append(np.var(block))

    block_vars = np.array(block_vars)

    return {
        "block_variance_mean": float(np.mean(block_vars)),
        "block_variance_std": float(np.std(block_vars)),
        "block_variance_global": float(np.var(block_vars))
    }


def intensity_features(gray):

    hist, _ = np.histogram(gray, bins=256, range=(0,255))

    hist = hist / np.sum(hist)

    entropy = -np.sum(hist * np.log2(hist + 1e-9))

    return {
        "mean_intensity": float(np.mean(gray)),
        "intensity_std": float(np.std(gray)),
        "intensity_entropy": float(entropy)
    }


def visual_artifacts_analysis(pil_image: Image.Image):

    gray = np.array(pil_image.convert("L")).astype("float")

    result = {
        "visual_artifact_features": {
            "fft": fft_features(gray),
            "noise": noise_features(gray),
            "gradient": gradient_features(gray),
            "edges": edge_features(gray),
            "symmetry": symmetry_features(gray),
            "texture_blocks": texture_block_features(gray),
            "intensity": intensity_features(gray)
        }
    }

    return result


def process(image_bytes):
    result = visual_artifacts_analysis(image_bytes)
    # return json.dumps(result, indent=2)
    return result