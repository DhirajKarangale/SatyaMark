import json

import numpy as np
from PIL import Image
from io import BytesIO


# -------------------------
# LOAD IMAGE
# -------------------------
def load_image(image_bytes):

    img = Image.open(BytesIO(image_bytes)).convert("RGB")

    img = np.asarray(img).astype(np.float32) / 255.0

    return img


# -------------------------
# ADD GAUSSIAN NOISE
# -------------------------
def add_noise(image, sigma):

    noise = np.random.normal(0, sigma, image.shape)

    noisy = image + noise

    return np.clip(noisy, 0, 1)


# -------------------------
# SIMPLE GRADIENT FEATURES
# (HOG-like but lightweight)
# -------------------------
def gradient_features(gray):

    gx = gray[:, 1:] - gray[:, :-1]
    gy = gray[1:, :] - gray[:-1, :]

    gx = gx[:-1, :]
    gy = gy[:, :-1]

    magnitude = np.sqrt(gx**2 + gy**2)

    return np.array([
        np.mean(magnitude),
        np.std(magnitude),
        np.var(magnitude)
    ])


# -------------------------
# FFT FEATURES
# -------------------------
def fft_features(gray):

    fft = np.fft.fft2(gray)

    fft = np.abs(fft)

    fft = np.log1p(fft)

    return np.array([
        np.mean(fft),
        np.std(fft),
        np.var(fft)
    ])


# -------------------------
# COLOR STATISTICS
# -------------------------
def color_features(image):

    r = image[:, :, 0]
    g = image[:, :, 1]
    b = image[:, :, 2]

    return np.array([
        np.mean(r), np.std(r),
        np.mean(g), np.std(g),
        np.mean(b), np.std(b)
    ])


# -------------------------
# EMBEDDING
# -------------------------
def generate_embedding(image):

    gray = np.mean(image, axis=2)

    grad = gradient_features(gray)

    freq = fft_features(gray)

    color = color_features(image)

    embedding = np.concatenate([grad, freq, color])

    return embedding


# -------------------------
# COSINE SIMILARITY
# -------------------------
def cosine_similarity(a, b):

    dot = np.dot(a, b)

    norm = np.linalg.norm(a) * np.linalg.norm(b)

    return dot / (norm + 1e-12)


# -------------------------
# PERTURBATION TEST
# -------------------------
def perturbation_robustness_test(image_bytes):

    image = load_image(image_bytes)

    base_embedding = generate_embedding(image)

    noise_levels = [
        0.001,
        0.003,
        0.005,
        0.01,
        0.02
    ]

    similarities = []

    for sigma in noise_levels:

        noisy = add_noise(image, sigma)

        emb = generate_embedding(noisy)

        sim = cosine_similarity(base_embedding, emb)

        similarities.append(sim)

    similarities = np.array(similarities)

    return {
        "perturbation_robustness": {
            "mean_similarity": float(np.mean(similarities)),
            "min_similarity": float(np.min(similarities)),
            "std_similarity": float(np.std(similarities)),
            "similarity_curve": similarities.tolist(),
            "noise_levels": noise_levels,
            "embedding_size": int(len(base_embedding))
        }
    }

def process(image_bytes):
    result = perturbation_robustness_test(image_bytes)
    # return json.dumps(result, indent=2)
    return result