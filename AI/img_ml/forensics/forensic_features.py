# forensics/forensic_features.py
"""
Compute classical forensic signals:
- FFT spectral smoothness
- ELA features
- Noise residual energy (simple high-pass)
- Wavelet statistics
- JPEG quantization anomalies (approx)
- EXIF metadata presence

Output: dict of features and a normalized forensic_score ∈ [0,1]
"""
from PIL import Image
import numpy as np
import cv2
import pywt
import exifread
import io
from .ela import compute_ela_image

def _to_gray_float(img):
    if isinstance(img, np.ndarray):
        arr = img
    else:
        arr = np.array(Image.open(img).convert("L"))
    arr = arr.astype(np.float32) / 255.0
    return arr

def fft_spectral_smoothness(img):
    im = _to_gray_float(img)
    f = np.fft.fft2(im)
    fshift = np.fft.fftshift(f)
    mag = np.log1p(np.abs(fshift))
    # estimate radial profile and measure smoothness (variance)
    center = np.array(mag.shape) // 2
    y,x = np.indices(mag.shape)
    r = np.hypot(x - center[1], y - center[0]).astype(int)
    t = np.bincount(r.ravel(), mag.ravel())
    counts = np.bincount(r.ravel())
    radial = t / (counts + 1e-9)
    # smoothness: inverse of variance (more structure -> less smooth)
    var = float(np.nanvar(radial))
    score = 1.0 / (1.0 + var)
    return float(score)

def ela_features(img):
    ela = compute_ela_image(img)
    arr = np.array(ela).astype(np.float32)/255.0
    # features: mean, std, skewness (approx), max
    mean = float(arr.mean())
    std = float(arr.std())
    mx = float(arr.max())
    return {"ela_mean": mean, "ela_std": std, "ela_max": mx}

def noise_residual_energy(img):
    gray = _to_gray_float(img)
    # denoise via gaussian, residual is high-frequency
    blurred = cv2.GaussianBlur(gray, (5,5), 0)
    residual = gray - blurred
    energy = float(np.mean(np.abs(residual)))
    return energy

def wavelet_stats(img):
    gray = _to_gray_float(img)
    coeffs = pywt.wavedec2(gray, wavelet='db1', level=2)
    # stats over detail coeffs
    stats = {}
    for i, coeff in enumerate(coeffs[1:], start=1):
        cH, cV, cD = coeff
        stats[f"w{i}_mean"] = float(np.mean(np.abs(cH)))
        stats[f"w{i}_var"] = float(np.var(cH))
    # aggregate
    aggregated = float(np.mean([v for k,v in stats.items()]))
    return aggregated

def jpeg_quantization_anomaly(img_path):
    try:
        with open(img_path, 'rb') as f:
            tags = exifread.process_file(f, stop_tag="JPEGThumbnail")
            # presence of JPEG quantization table not trivially extractable via exifread;
            has_exif = len(tags) > 0
            return 0.0 if has_exif else 1.0
    except Exception:
        return 1.0

def exif_presence(img_path):
    try:
        with open(img_path, 'rb') as f:
            tags = exifread.process_file(f)
            return 1.0 if len(tags)>0 else 0.0
    except Exception:
        return 0.0

def compute_forensic_features(image_path):
    features = {}
    features["fft_smooth"] = fft_spectral_smoothness(image_path)
    ela_f = ela_features(image_path)
    features.update(ela_f)
    features["noise_energy"] = noise_residual_energy(image_path)
    features["wavelet_stat"] = wavelet_stats(image_path)
    features["jpeg_anomaly"] = jpeg_quantization_anomaly(image_path)
    features["exif_present"] = exif_presence(image_path)
    # Normalize to [0,1] via simple heuristics / clipping
    vals = []
    for k in features:
        v = features[k]
        # simple normalization heuristics
        if isinstance(v, (int, float)):
            vals.append(float(v))
    # scale to 0-1
    arr = np.array(vals)
    # robust minmax
    lo, hi = np.percentile(arr, [2,98])
    norm = (arr - lo) / (hi - lo + 1e-9)
    norm = np.clip(norm, 0.0, 1.0)
    # final forensic score: mean of normalized signals (higher means more suspicious)
    forensic_score = float(norm.mean())
    features["forensic_score"] = forensic_score
    return features
