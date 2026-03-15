import json
import numpy as np
import pywt
from PIL import Image
from io import BytesIO


def analyze_watermark(image_bytes):
    try:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        img_np = np.array(img)

        height, width, _ = img_np.shape

        # ---- grayscale ----
        gray = np.dot(img_np[..., :3], [0.299, 0.587, 0.114])

        # ---- wavelet decomposition ----
        coeffs = pywt.dwt2(gray, "haar")
        LL, (LH, HL, HH) = coeffs

        lh_energy = float(np.mean(np.abs(LH)))
        hl_energy = float(np.mean(np.abs(HL)))
        hh_energy = float(np.mean(np.abs(HH)))

        wavelet_score = (lh_energy + hl_energy + hh_energy) / 3

        # ---- FFT periodic structure detection ----
        fft = np.fft.fft2(gray)
        fft_shift = np.fft.fftshift(fft)
        magnitude = np.log(np.abs(fft_shift) + 1)

        fft_mean = float(np.mean(magnitude))
        fft_std = float(np.std(magnitude))
        fft_peak = float(np.max(magnitude))

        # periodic watermark indicator
        fft_score = fft_peak / (fft_mean + 1e-5)

        # ---- spatial noise pattern ----
        noise = gray - pywt.idwt2((LL, (LH, HL, HH)), "haar")

        noise_mean = float(np.mean(noise))
        noise_std = float(np.std(noise))

        # ---- block consistency (watermarks repeat patterns) ----
        block_size = 32
        blocks = []

        for y in range(0, height - block_size, block_size):
            for x in range(0, width - block_size, block_size):
                block = gray[y:y+block_size, x:x+block_size]
                blocks.append(np.mean(block))

        block_variance = float(np.var(blocks))

        # ---- combined watermark score ----
        watermark_score = (
            wavelet_score * 0.4 +
            fft_score * 0.4 +
            block_variance * 0.2
        )

        detected = watermark_score > 5

        return {
            "watermark_analysis": {
                "watermark_detected": bool(detected),
                "watermark_score": float(watermark_score)
            },

            "wavelet_features": {
                "lh_energy": lh_energy,
                "hl_energy": hl_energy,
                "hh_energy": hh_energy,
                "wavelet_score": wavelet_score
            },

            "fft_features": {
                "fft_mean": fft_mean,
                "fft_std": fft_std,
                "fft_peak": fft_peak,
                "fft_periodicity_score": fft_score
            },

            "noise_features": {
                "noise_mean": noise_mean,
                "noise_std": noise_std
            },

            "block_pattern_features": {
                "block_variance": block_variance
            },

            "image_info": {
                "width": width,
                "height": height
            }
        }

    except Exception as e:
        return {"error": str(e)}


def process(image_bytes):
    result = analyze_watermark(image_bytes)
    # return json.dumps(result, indent=2)
    return result