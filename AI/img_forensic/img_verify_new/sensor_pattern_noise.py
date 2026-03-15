import numpy as np
import json
import pywt


def wavelet_denoise(image):
    coeffs = pywt.wavedec2(image, "db4", level=4)

    denoised_coeffs = []

    for i, coeff in enumerate(coeffs):
        if i == 0:
            denoised_coeffs.append(coeff)
        else:
            cH, cV, cD = coeff

            cH = pywt.threshold(cH, np.std(cH), mode="soft")
            cV = pywt.threshold(cV, np.std(cV), mode="soft")
            cD = pywt.threshold(cD, np.std(cD), mode="soft")

            denoised_coeffs.append((cH, cV, cD))

    denoised = pywt.waverec2(denoised_coeffs, "db4")

    return denoised[: image.shape[0], : image.shape[1]]


def extract_noise_residual(image):
    denoised = wavelet_denoise(image)
    noise = image - denoised
    return noise


def correlation(a, b):
    a = a.flatten()
    b = b.flatten()

    a_mean = np.mean(a)
    b_mean = np.mean(b)

    numerator = np.sum((a - a_mean) * (b - b_mean))
    denominator = np.sqrt(np.sum((a - a_mean) ** 2) * np.sum((b - b_mean) ** 2))

    if denominator == 0:
        return 0.0

    return float(numerator / denominator)


def compute_spn_metrics(gray_pixels):
    spn = extract_noise_residual(gray_pixels)

    energy = float(np.mean(spn ** 2))

    row_variance = float(np.mean(np.var(spn, axis=1)))
    column_variance = float(np.mean(np.var(spn, axis=0)))

    horizontal_corr = correlation(spn[:, :-1], spn[:, 1:])
    vertical_corr = correlation(spn[:-1, :], spn[1:, :])

    return {
        "spn_shape": list(spn.shape),
        "spn_metrics": {
            "energy": energy,
            "row_variance": row_variance,
            "column_variance": column_variance,
            "horizontal_correlation": horizontal_corr,
            "vertical_correlation": vertical_corr
        }
    }


def run_spn(gray_pixels):
    return compute_spn_metrics(gray_pixels)


def process(image_bytes):
    result = run_spn(image_bytes)
    # return json.dumps(result, indent=2)
    return result