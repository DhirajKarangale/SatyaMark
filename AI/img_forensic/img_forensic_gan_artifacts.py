import cv2
import base64
import numpy as np


def normalize_score(v, scale=100.0):
    try:
        v = float(v)
        return float(min(max(v / scale, 0.0), 1.0))
    except:
        return 0.0


def encode_heatmap(img):
    try:
        _, buf = cv2.imencode(".jpg", img)
        return base64.b64encode(buf).decode("utf-8")
    except:
        return None


def feature_texture_repetition(gray):
    """Measures repeating texture using auto-correlation."""
    try:
        h, w = gray.shape
        patch = gray[h // 4 : h // 4 * 3, w // 4 : w // 4 * 3]
        ac = cv2.matchTemplate(patch, patch, cv2.TM_CCORR_NORMED)
        return normalize_score(np.mean(ac) * 100)
    except:
        return 0.0


def feature_sampling_artifacts(gray):
    """Measures high-frequency diffusion-like noise using FFT."""
    try:
        fft = np.fft.fftshift(np.fft.fft2(gray))
        mag = np.log(np.abs(fft) + 1e-12)
        hf = mag[
            mag.shape[0] // 4 : -mag.shape[0] // 4,
            mag.shape[1] // 4 : -mag.shape[1] // 4,
        ]
        return normalize_score(np.mean(hf) * 5)
    except:
        return 0.0


def feature_upscale_traces(gray):
    """Detect sharp grid-like edges produced by AI upscalers."""
    try:
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1)
        edges = np.abs(sobel_x) + np.abs(sobel_y)
        return normalize_score(np.mean(edges) * 0.2)
    except:
        return 0.0


def feature_pattern_periodicity(gray):
    """Detect periodic GAN patterns using FFT radial standard deviation."""
    try:
        fft = np.abs(np.fft.fft2(gray))
        freq = np.mean(fft, axis=0)
        periodicity = np.std(freq)
        return normalize_score(periodicity * 0.05)
    except:
        return 0.0


def generate_heatmap_preview(gray):
    try:
        heat = cv2.applyColorMap(cv2.convertScaleAbs(gray, alpha=0.5), cv2.COLORMAP_JET)
        return encode_heatmap(heat)
    except:
        return None


def gan_artifacts_analyze(image_path):
    img = cv2.imread(image_path)
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        texture_repetition = feature_texture_repetition(gray)
        sampling_artifacts = feature_sampling_artifacts(gray)
        upscale_traces = feature_upscale_traces(gray)
        pattern_periodicity = feature_pattern_periodicity(gray)
        heatmap_preview = generate_heatmap_preview(gray)

        artifact_score = float(
            texture_repetition * 0.25
            + sampling_artifacts * 0.35
            + upscale_traces * 0.20
            + pattern_periodicity * 0.20
        )

        result = {
            "gan_artifacts": {
                "status": "ok",
                "artifact_score": round(artifact_score, 4),
                "details": {
                    "texture_repetition": texture_repetition,
                    "sampling_artifacts": sampling_artifacts,
                    "upscale_traces": upscale_traces,
                    "pattern_periodicity": pattern_periodicity,
                    # "heatmap_preview": heatmap_preview
                },
                "notes": "",
            }
        }

        return result

    except Exception as e:
        return {
            "gan_artifacts": {
                "status": "error",
                "artifact_score": 0.0,
                "details": {
                    "texture_repetition": 0.0,
                    "sampling_artifacts": 0.0,
                    "upscale_traces": 0.0,
                    "pattern_periodicity": 0.0,
                    "heatmap_preview": None,
                },
                "notes": str(e),
            }
        }
