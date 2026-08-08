import json
import numpy as np
from PIL import Image
from io import BytesIO


def load_image(image_data):

    if isinstance(image_data, bytes):
        img = Image.open(BytesIO(image_data))
    elif isinstance(image_data, str):
        img = Image.open(image_data)
    else:
        raise ValueError("Unsupported image input")

    img = img.convert("L")
    img = np.array(img).astype(np.float32) / 255.0
    return img


# -----------------------------
# SIMPLE PEAK DETECTOR
# -----------------------------

def find_peaks(signal, height):

    peaks = []
    n = len(signal)

    for i in range(1, n - 1):
        if signal[i] > signal[i-1] and signal[i] > signal[i+1] and signal[i] > height:
            peaks.append(i)

    return peaks


# -----------------------------
# PATCH GENERATOR
# -----------------------------

def extract_patches(img, patch_size=128, stride=64):

    h, w = img.shape
    patches = []

    for y in range(0, h - patch_size, stride):
        for x in range(0, w - patch_size, stride):
            patches.append(img[y:y+patch_size, x:x+patch_size])

    return patches


# -----------------------------
# GAN CHECKERBOARD DETECTION
# -----------------------------

def checkerboard_score_patch(patch):

    f = np.fft.fft2(patch)
    fshift = np.fft.fftshift(f)
    spectrum = np.log(np.abs(fshift) + 1e-8)

    h, w = spectrum.shape
    cy, cx = h // 2, w // 2

    spectrum[cy-5:cy+5, cx-5:cx+5] = 0

    horiz = spectrum[cy]
    vert = spectrum[:, cx]

    threshold_h = np.mean(horiz) * 2
    threshold_v = np.mean(vert) * 2

    peaks_h = find_peaks(horiz, threshold_h)
    peaks_v = find_peaks(vert, threshold_v)

    return len(peaks_h) + len(peaks_v)


def detect_gan_checkerboard(img):

    patches = extract_patches(img)

    scores = []

    for p in patches:
        scores.append(checkerboard_score_patch(p))

    scores = np.array(scores)

    return {
        "mean_checker_peaks": float(np.mean(scores)),
        "max_checker_peaks": int(np.max(scores)),
        "checker_variance": float(np.var(scores))
    }


# -----------------------------
# DIFFUSION ARTIFACT DETECTION
# -----------------------------

def radial_profile(spectrum):

    h, w = spectrum.shape
    cy, cx = h // 2, w // 2

    y, x = np.ogrid[:h, :w]
    r = np.sqrt((x-cx)**2 + (y-cy)**2)

    r = r.astype(np.int32)

    radial_sum = np.bincount(r.ravel(), spectrum.ravel())
    radial_count = np.bincount(r.ravel())

    radial_mean = radial_sum / (radial_count + 1e-8)

    return radial_mean


def diffusion_artifacts(img):

    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    spectrum = np.abs(fshift)

    radial = radial_profile(spectrum)

    threshold = np.mean(radial) * 1.5
    peaks = find_peaks(radial, threshold)

    return {
        "radial_std": float(np.std(radial)),
        "radial_peak_count": int(len(peaks)),
        "radial_peak_density": float(len(peaks) / len(radial)),
        "radial_energy": float(np.sum(radial))
    }


# -----------------------------
# MAIN PIPELINE
# -----------------------------

def detect_gan_diffusion_artifacts(image_data):

    img = load_image(image_data)

    gan = detect_gan_checkerboard(img)
    diffusion = diffusion_artifacts(img)

    return {
        "gan_checkerboard_artifacts": gan,
        "diffusion_sampling_artifacts": diffusion
    }


def process(image_bytes):
    result = detect_gan_diffusion_artifacts(image_bytes)
    # return json.dumps(result, indent=2)
    return result