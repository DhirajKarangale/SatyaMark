import json
import numpy as np
import pywt
from PIL import Image
from io import BytesIO


# ------------------------------------------------
# Image Loader
# ------------------------------------------------

def load_image(image_bytes):
    img = Image.open(BytesIO(image_bytes)).convert("L")
    return np.array(img, dtype=np.float32)


# ------------------------------------------------
# FFT Spectrum
# ------------------------------------------------

def compute_fft(image):
    fft = np.fft.fft2(image)
    fft_shift = np.fft.fftshift(fft)
    spectrum = np.log1p(np.abs(fft_shift))
    return spectrum


# ------------------------------------------------
# Radial Spectrum
# ------------------------------------------------

def radial_profile(data):

    h, w = data.shape
    y, x = np.indices((h, w))

    center = np.array([h//2, w//2])

    r = np.sqrt((x-center[1])**2 + (y-center[0])**2).astype(np.int32)

    tbin = np.bincount(r.ravel(), data.ravel())
    nr = np.bincount(r.ravel())

    radial = tbin / np.maximum(nr, 1)

    return radial


# ------------------------------------------------
# Frequency Energy Distribution
# ------------------------------------------------

def frequency_energy_zones(spec):

    h, w = spec.shape
    cy, cx = h//2, w//2

    y, x = np.ogrid[:h, :w]
    dist = np.sqrt((x-cx)**2 + (y-cy)**2)

    r1 = min(cx, cy) * 0.15
    r2 = min(cx, cy) * 0.45

    low = spec[dist <= r1].sum()
    mid = spec[(dist > r1) & (dist <= r2)].sum()
    high = spec[dist > r2].sum()

    total = low + mid + high + 1e-12

    return float(low/total), float(mid/total), float(high/total)


# ------------------------------------------------
# Spectral Metrics
# ------------------------------------------------

def spectral_entropy(spec):

    p = spec / np.sum(spec)
    p = p + 1e-12

    return float(-np.sum(p * np.log2(p)))


def spectral_centroid(spec):

    h, w = spec.shape
    y, x = np.indices(spec.shape)

    cy, cx = h//2, w//2

    dist = np.sqrt((x-cx)**2 + (y-cy)**2)

    return float(np.sum(dist * spec) / np.sum(spec))


def spectral_flatness(spec):

    spec = spec + 1e-12

    geo = np.exp(np.mean(np.log(spec)))
    arith = np.mean(spec)

    return float(geo / arith)


# ------------------------------------------------
# Artifact Indicators
# ------------------------------------------------

def peak_density(spec):

    mean = np.mean(spec)
    std = np.std(spec)

    peaks = spec > (mean + 3*std)

    return float(np.sum(peaks) / spec.size)


def ring_artifact_score(radial):

    diff = np.diff(radial)

    return float(np.std(diff))


def axis_energy_imbalance(spec):

    vertical = np.sum(np.abs(np.diff(spec, axis=0)))
    horizontal = np.sum(np.abs(np.diff(spec, axis=1)))

    return float(abs(vertical-horizontal) / (vertical+horizontal+1e-12))


# ------------------------------------------------
# Wavelet Texture Analysis
# ------------------------------------------------

def wavelet_analysis(image):

    LL, (LH, HL, HH) = pywt.dwt2(image, "haar")

    e_ll = np.sum(np.abs(LL))
    e_lh = np.sum(np.abs(LH))
    e_hl = np.sum(np.abs(HL))
    e_hh = np.sum(np.abs(HH))

    total = e_ll + e_lh + e_hl + e_hh + 1e-12

    return {
        "ll_ratio": float(e_ll/total),
        "lh_ratio": float(e_lh/total),
        "hl_ratio": float(e_hl/total),
        "hh_ratio": float(e_hh/total)
    }


# ------------------------------------------------
# DCT Block Grid Analysis
# ------------------------------------------------

def dct_grid_analysis(image):

    h, w = image.shape

    h -= h % 8
    w -= w % 8

    image = image[:h, :w]

    energies = []

    for i in range(0, h, 8):
        for j in range(0, w, 8):

            block = image[i:i+8, j:j+8]

            dct = np.fft.fft2(block)

            energies.append(np.sum(np.abs(dct)))

    energies = np.array(energies)

    return {
        "block_energy_mean": float(np.mean(energies)),
        "block_energy_std": float(np.std(energies))
    }


# ------------------------------------------------
# Noise Residual Analysis
# ------------------------------------------------

def noise_analysis(image):

    blur = (
        image[:-2,1:-1] +
        image[2:,1:-1] +
        image[1:-1,:-2] +
        image[1:-1,2:]
    ) / 4

    residual = image[1:-1,1:-1] - blur

    return {
        "noise_mean": float(np.mean(residual)),
        "noise_std": float(np.std(residual)),
        "noise_variance": float(np.var(residual))
    }


# ------------------------------------------------
# Main Forensic Pipeline
# ------------------------------------------------

def forensic_analysis(image_bytes):

    img = load_image(image_bytes)

    spec = compute_fft(img)

    radial = radial_profile(spec)

    low, mid, high = frequency_energy_zones(spec)

    result = {

        "frequency_analysis": {

            "low_frequency_ratio": low,
            "mid_frequency_ratio": mid,
            "high_frequency_ratio": high,

            "spectral_entropy": spectral_entropy(spec),
            "spectral_centroid": spectral_centroid(spec),
            "spectral_flatness": spectral_flatness(spec),

            "peak_density": peak_density(spec),
            "ring_artifact_score": ring_artifact_score(radial),
            "axis_energy_imbalance": axis_energy_imbalance(spec),

            "radial_power_spectrum_sample": radial[:40].tolist()
        },

        "wavelet_analysis": wavelet_analysis(img),

        "dct_analysis": dct_grid_analysis(img),

        "noise_analysis": noise_analysis(img)
    }

    return result


def process(image_bytes):
    result = forensic_analysis(image_bytes)
    # return json.dumps(result, indent=2)
    return result