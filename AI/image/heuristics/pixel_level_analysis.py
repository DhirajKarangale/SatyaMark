import json
import numpy as np
from PIL import Image
from io import BytesIO


def load_image(image_bytes):
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    arr = np.asarray(img).astype(np.float32)
    return arr


def channel_stats(channel):
    return {
        "mean": float(np.mean(channel)),
        "std": float(np.std(channel)),
        "variance": float(np.var(channel)),
        "min": float(np.min(channel)),
        "max": float(np.max(channel)),
    }


def skewness(channel):
    m = np.mean(channel)
    s = np.std(channel)
    if s == 0:
        return 0.0
    return float(np.mean(((channel - m) / s) ** 3))


def kurtosis(channel):
    m = np.mean(channel)
    s = np.std(channel)
    if s == 0:
        return 0.0
    return float(np.mean(((channel - m) / s) ** 4) - 3)


def entropy(channel):
    hist, _ = np.histogram(channel, bins=256, range=(0, 255), density=True)
    hist = hist + 1e-12
    return float(-np.sum(hist * np.log2(hist)))


def color_correlation(r, g, b):
    return {
        "rg_corr": float(np.corrcoef(r.flatten(), g.flatten())[0, 1]),
        "rb_corr": float(np.corrcoef(r.flatten(), b.flatten())[0, 1]),
        "gb_corr": float(np.corrcoef(g.flatten(), b.flatten())[0, 1]),
    }


def neighbor_correlation(channel):
    horiz = np.corrcoef(channel[:, :-1].flatten(), channel[:, 1:].flatten())[0, 1]
    vert = np.corrcoef(channel[:-1, :].flatten(), channel[1:, :].flatten())[0, 1]
    diag = np.corrcoef(channel[:-1, :-1].flatten(), channel[1:, 1:].flatten())[0, 1]

    return {
        "horizontal": float(horiz),
        "vertical": float(vert),
        "diagonal": float(diag),
    }


def pixel_difference_stats(channel):
    dx = channel[:, 1:] - channel[:, :-1]
    dy = channel[1:, :] - channel[:-1, :]

    diffs = np.concatenate([dx.flatten(), dy.flatten()])

    return {
        "mean": float(np.mean(diffs)),
        "std": float(np.std(diffs)),
        "entropy": float(entropy(diffs)),
    }


def residual_noise(img):
    blurred = (img[:-2, :-2] + img[1:-1, :-2] + img[2:, :-2] +
               img[:-2, 1:-1] + img[1:-1, 1:-1] + img[2:, 1:-1] +
               img[:-2, 2:] + img[1:-1, 2:] + img[2:, 2:]) / 9.0

    center = img[1:-1, 1:-1]
    residual = center - blurred

    return {
        "mean": float(np.mean(residual)),
        "std": float(np.std(residual)),
        "kurtosis": float(np.mean(((residual - np.mean(residual)) /
                     (np.std(residual) + 1e-8)) ** 4) - 3),
    }


def laplacian_stats(channel):
    lap = (
        -4 * channel[1:-1, 1:-1]
        + channel[:-2, 1:-1]
        + channel[2:, 1:-1]
        + channel[1:-1, :-2]
        + channel[1:-1, 2:]
    )

    return {
        "mean": float(np.mean(lap)),
        "std": float(np.std(lap)),
        "variance": float(np.var(lap)),
    }


def gradient_stats(channel):
    gx = channel[:, 1:] - channel[:, :-1]
    gy = channel[1:, :] - channel[:-1, :]

    grad = np.sqrt(gx[:-1] ** 2 + gy[:, :-1] ** 2)

    return {
        "mean": float(np.mean(grad)),
        "std": float(np.std(grad)),
        "energy": float(np.sum(grad ** 2) / grad.size),
    }


def clipping_ratio(channel):
    total = channel.size

    zeros = np.sum(channel == 0)
    maxs = np.sum(channel == 255)

    return {
        "zero_ratio": float(zeros / total),
        "max_ratio": float(maxs / total),
    }


def channel_difference(r, g, b):
    rg = r - g
    bg = b - g

    return {
        "rg_mean": float(np.mean(rg)),
        "rg_std": float(np.std(rg)),
        "bg_mean": float(np.mean(bg)),
        "bg_std": float(np.std(bg)),
    }


def local_variance(channel, window=5):
    pad = window // 2
    padded = np.pad(channel, pad, mode="reflect")

    variances = []

    for i in range(channel.shape[0]):
        for j in range(channel.shape[1]):
            patch = padded[i:i+window, j:j+window]
            variances.append(np.var(patch))

    variances = np.array(variances)

    return {
        "mean": float(np.mean(variances)),
        "std": float(np.std(variances)),
        "min": float(np.min(variances)),
        "max": float(np.max(variances)),
    }


def pixel_forensic_analysis(image_bytes):

    img = load_image(image_bytes)

    r = img[:, :, 0]
    g = img[:, :, 1]
    b = img[:, :, 2]

    gray = 0.299*r + 0.587*g + 0.114*b

    result = {

        "channel_statistics": {
            "red": channel_stats(r),
            "green": channel_stats(g),
            "blue": channel_stats(b),
        },

        "skewness": {
            "r": skewness(r),
            "g": skewness(g),
            "b": skewness(b),
        },

        "kurtosis": {
            "r": kurtosis(r),
            "g": kurtosis(g),
            "b": kurtosis(b),
        },

        "entropy": {
            "r": entropy(r),
            "g": entropy(g),
            "b": entropy(b),
        },

        "color_correlation": color_correlation(r, g, b),

        "neighbor_correlation": neighbor_correlation(gray),

        "pixel_difference": pixel_difference_stats(gray),

        "residual_noise": residual_noise(gray),

        "laplacian_statistics": laplacian_stats(gray),

        "gradient_statistics": gradient_stats(gray),

        "pixel_clipping": clipping_ratio(gray),

        "channel_difference_statistics": channel_difference(r, g, b),

        "local_variance": local_variance(gray),
    }

    return result


def process(image_bytes):
    result = pixel_forensic_analysis(image_bytes)
    # return json.dumps(result, indent=2)
    return result