import json
import numpy as np
from PIL import Image
from io import BytesIO
from scipy.fftpack import dct


# ----------------------------------------------------------
# 8x8 DCT transform
# ----------------------------------------------------------
def block_dct(block):
    return dct(dct(block.T, norm="ortho").T, norm="ortho")


# ----------------------------------------------------------
# Extract DCT blocks
# ----------------------------------------------------------
def extract_dct_blocks(gray):

    h, w = gray.shape
    h -= h % 8
    w -= w % 8

    blocks = []

    for y in range(0, h, 8):
        for x in range(0, w, 8):

            block = gray[y:y+8, x:x+8].astype(np.float32)

            block = block * 255.0
            block -= 128.0

            blocks.append(block_dct(block))

    return blocks


# ----------------------------------------------------------
# JPEG blockiness metric (normalized)
# ----------------------------------------------------------
def jpeg_blockiness_metric(gray):

    h, w = gray.shape

    boundary_diffs = []
    natural_diffs = []

    for i in range(1, w):

        diff = np.abs(gray[:, i] - gray[:, i-1]).mean()

        if i % 8 == 0:
            boundary_diffs.append(diff)
        else:
            natural_diffs.append(diff)

    for j in range(1, h):

        diff = np.abs(gray[j, :] - gray[j-1, :]).mean()

        if j % 8 == 0:
            boundary_diffs.append(diff)
        else:
            natural_diffs.append(diff)

    boundary = np.mean(boundary_diffs) if boundary_diffs else 0
    natural = np.mean(natural_diffs) if natural_diffs else 1

    return float(boundary / (natural + 1e-8))


# ----------------------------------------------------------
# Blocking artifact strength
# ----------------------------------------------------------
def blocking_artifact_score(gray):

    h, w = gray.shape

    vertical_scores = []
    horizontal_scores = []

    for i in range(8, w, 8):
        vertical_scores.append(np.mean(np.abs(gray[:, i] - gray[:, i-1])))

    for j in range(8, h, 8):
        horizontal_scores.append(np.mean(np.abs(gray[j, :] - gray[j-1, :])))

    v = np.mean(vertical_scores) if vertical_scores else 0
    h = np.mean(horizontal_scores) if horizontal_scores else 0

    return float(v), float(h)


# ----------------------------------------------------------
# DCT statistics
# ----------------------------------------------------------
def dct_statistics(dct_blocks):

    coeffs = np.array(dct_blocks).flatten()

    mean = np.mean(coeffs)
    std = np.std(coeffs)

    kurtosis = np.mean((coeffs - mean) ** 4) / ((std ** 4) + 1e-8)

    return {
        "mean": float(mean),
        "std": float(std),
        "variance": float(np.var(coeffs)),
        "kurtosis": float(kurtosis),
        "energy": float(np.mean(coeffs ** 2))
    }


# ----------------------------------------------------------
# Zero coefficient ratio
# ----------------------------------------------------------
def dct_zero_ratio(dct_blocks):

    coeffs = np.array(dct_blocks).flatten()

    zero_count = np.sum(np.abs(coeffs) < 1e-6)

    return float(zero_count / len(coeffs))


# ----------------------------------------------------------
# Quantization periodicity
# ----------------------------------------------------------
def quantization_periodicity(dct_blocks):

    coeffs = np.array(dct_blocks).flatten()

    spectrum = np.abs(np.fft.fft(coeffs))

    periodicity = np.max(spectrum[1:]) / (np.sum(spectrum) + 1e-8)

    return float(periodicity)


# ----------------------------------------------------------
# Double JPEG compression detector
# ----------------------------------------------------------
def double_jpeg_detector(dct_blocks):

    coeffs = np.array(dct_blocks).flatten()

    hist, _ = np.histogram(coeffs, bins=200)

    peak_count = np.sum(hist > np.mean(hist) * 2)

    return float(peak_count / len(hist))


# ----------------------------------------------------------
# Block boundary variance difference
# ----------------------------------------------------------
def block_boundary_variance(gray):

    h, w = gray.shape

    boundary_pixels = []
    natural_pixels = []

    for i in range(1, w):

        diff = np.abs(gray[:, i] - gray[:, i-1])

        if i % 8 == 0:
            boundary_pixels.extend(diff)
        else:
            natural_pixels.extend(diff)

    for j in range(1, h):

        diff = np.abs(gray[j, :] - gray[j-1, :])

        if j % 8 == 0:
            boundary_pixels.extend(diff)
        else:
            natural_pixels.extend(diff)

    boundary_var = np.var(boundary_pixels) if boundary_pixels else 0
    natural_var = np.var(natural_pixels) if natural_pixels else 1

    return float(boundary_var / (natural_var + 1e-8))


# ----------------------------------------------------------
# Main Compression Artifact Analysis
# ----------------------------------------------------------
def compression_artifact_analysis(image_bytes):

    image = Image.open(BytesIO(image_bytes))

    image_format = image.format

    # normalize grayscale to 0-1 (fix for blocking score scaling)
    gray = np.array(image.convert("L")).astype(np.float32) / 255.0

    # extract DCT blocks
    dct_blocks = extract_dct_blocks(gray)

    jpeg_blockiness = jpeg_blockiness_metric(gray)

    vertical_block, horizontal_block = blocking_artifact_score(gray)

    stats = dct_statistics(dct_blocks)

    zero_ratio = dct_zero_ratio(dct_blocks)

    periodicity = quantization_periodicity(dct_blocks)

    double_jpeg = double_jpeg_detector(dct_blocks)

    boundary_variance = block_boundary_variance(gray)

    return {
        "compression_analysis": {

            "image_format": image_format,

            "jpeg_blockiness_ratio": jpeg_blockiness,

            "blocking_artifacts": {
                "vertical_blocking_score": vertical_block,
                "horizontal_blocking_score": horizontal_block
            },

            "dct_statistics": stats,

            "dct_zero_ratio": zero_ratio,

            "quantization_periodicity": periodicity,

            "double_jpeg_probability": double_jpeg,

            "block_boundary_variance_ratio": boundary_variance,

            "dct_block_count": len(dct_blocks)
        }
    }

def process(image_bytes):
    result = compression_artifact_analysis(image_bytes)
    # return json.dumps(result, indent=2)
    return result