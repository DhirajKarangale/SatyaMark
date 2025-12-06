import cv2
import pywt
import traceback
import numpy as np

EPS = 1e-12


def skewness(arr):
    a = arr.flatten()
    m = a.mean()
    s = a.std(ddof=0) + EPS
    return float(((a - m) ** 3).mean() / (s**3))


def kurtosis(arr):
    a = arr.flatten()
    m = a.mean()
    s = a.std(ddof=0) + EPS
    return float(((a - m) ** 4).mean() / (s**4) - 3.0)


def extract_prnu(gray):
    try:
        coeffs = pywt.wavedec2(gray, "db2", level=2)
        coeffs_hp = list(coeffs)
        coeffs_hp[0] = np.zeros_like(coeffs_hp[0])

        hp = pywt.waverec2(coeffs_hp, "db2")
        hp = cv2.resize(hp, (gray.shape[1], gray.shape[0]))
        hp = hp.astype(np.float32)
        hp -= np.mean(hp)

        return hp
    except:
        return None


def prnu_metrics(prnu):
    if prnu is None:
        return {"prnu_std": 0.0, "prnu_energy": 0.0, "prnu_mean_abs": 0.0}

    return {
        "prnu_std": float(np.std(prnu)),
        "prnu_energy": float(np.sum(prnu.astype(np.float64) ** 2)),
        "prnu_mean_abs": float(np.mean(np.abs(prnu))),
    }


def extract_patches(gray, count=6):
    h, w = gray.shape
    ph, pw = h // 4, w // 4

    coords = [
        (0, 0),
        (0, w - pw),
        (h - ph, 0),
        (h - ph, w - pw),
        (h // 2, w // 2),
        (h // 4, w // 4),
    ]

    patches = []
    for y, x in coords[:count]:
        patch = gray[y : y + ph, x : x + pw]
        if patch.size > 0:
            patches.append(patch)

    return patches


def correlation(a, b):
    a = a.flatten().astype(np.float64)
    b = b.flatten().astype(np.float64)

    a -= a.mean()
    b -= b.mean()

    denom = (np.sqrt((a * a).sum()) * np.sqrt((b * b).sum())) + EPS
    return float((a * b).sum() / denom)


def prnu_patch_correlations(full_prnu, patches):
    corrs = []
    for p in patches:
        p_prnu = extract_prnu(p.astype(np.float32))
        if p_prnu is None:
            continue

        p_up = cv2.resize(p_prnu, (full_prnu.shape[1], full_prnu.shape[0]))
        corrs.append(correlation(full_prnu, p_up))

    return corrs


def cfa_metrics(img):
    try:
        b = img[:, :, 0].astype(np.float32)
        g = img[:, :, 1].astype(np.float32)
        r = img[:, :, 2].astype(np.float32)

        rg = correlation(r, g)
        gb = correlation(g, b)
        avg = (rg + gb) / 2.0

        return {
            "cfa_rg_corr": float(rg),
            "cfa_gb_corr": float(gb),
            "cfa_pattern_consistency": float(avg),
        }
    except:
        return {
            "cfa_rg_corr": 0.0,
            "cfa_gb_corr": 0.0,
            "cfa_pattern_consistency": 0.0,
        }


def statistical_metrics(prnu):
    if prnu is None:
        return {"skewness": 0.0, "kurtosis": 0.0, "spectral_slope": 0.0}

    try:
        f = np.fft.fft2(prnu)
        fshift = np.fft.fftshift(f)
        ps = np.abs(fshift) ** 2 + EPS

        h, w = ps.shape
        cy, cx = h // 2, w // 2

        y = np.arange(h) - cy
        x = np.arange(w) - cx
        xv, yv = np.meshgrid(x, y)
        r = np.sqrt(xv**2 + yv**2)

        low = ps[r < r.max() * 0.1].mean()
        high = ps[r > r.max() * 0.6].mean()

        slope = float(np.log(high + EPS) - np.log(low + EPS))
    except:
        slope = 0.0

    return {
        "skewness": float(skewness(prnu)),
        "kurtosis": float(kurtosis(prnu)),
        "spectral_slope": slope,
    }


def mobile_dslr_likelihood(prnu_m, cfa_m):
    return {
        "mobile_camera_likelihood_raw": float(
            prnu_m["prnu_mean_abs"] * 5.0 + (1 - cfa_m["cfa_pattern_consistency"]) * 2.0
        ),
        "dslr_camera_likelihood_raw": float(
            prnu_m["prnu_energy"] / (1 + prnu_m["prnu_energy"]) * 5.0
            + cfa_m["cfa_pattern_consistency"] * 2.0
        ),
    }


def sensor_fingerprint_analyze(image_path):
    img = cv2.imread(image_path)
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)

        prnu = extract_prnu(gray)
        prnu_m = prnu_metrics(prnu)

        patches = extract_patches(gray)
        patch_corrs = prnu_patch_correlations(prnu, patches)

        cfa_m = cfa_metrics(img)
        stat_m = statistical_metrics(prnu)
        cam_m = mobile_dslr_likelihood(prnu_m, cfa_m)

        result = {
            "sensor_fingerprint": {
                "status": "ok",
                "details": {
                    **prnu_m,
                    "patch_correlations": patch_corrs,
                    "patch_correlation_avg": float(np.mean(patch_corrs)),
                    "patch_correlation_std": float(np.std(patch_corrs)),
                    **cfa_m,
                    "prnu_skewness": stat_m["skewness"],
                    "prnu_kurtosis": stat_m["kurtosis"],
                    "prnu_spectral_slope": stat_m["spectral_slope"],
                    **cam_m,
                },
            }
        }

        return result

    except Exception as e:
        return {
            "sensor_fingerprint": {
                "status": "error",
                "details": {},
                "notes": str(e) + traceback.format_exc(),
            }
        }
