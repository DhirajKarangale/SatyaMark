import json
import math

def detect(data):

    ai_score = 0
    real_score = 0
    reasons = []

    # -------------------
    # Metadata
    # -------------------
    meta = data["metadata"]["analysis"]

    if meta["has_exif"] and meta["camera_valid"]:
        real_score += 2
    else:
        ai_score += 1
        reasons.append("missing camera metadata")

    # -------------------
    # C2PA provenance
    # -------------------
    if data["c2pa"]["c2pa_present"] and data["c2pa"]["valid_signature"]:
        real_score += 3
        reasons.append("verified provenance signature")

    # -------------------
    # Sensor Pattern Noise
    # -------------------
    spn = data["sensor_pattern_noise"]["spn_metrics"]

    if spn["horizontal_correlation"] > 0.75 and spn["vertical_correlation"] > 0.75:
        real_score += 3
        reasons.append("strong camera sensor noise pattern")
    else:
        ai_score += 2
        reasons.append("weak sensor noise pattern")

    # -------------------
    # GAN artifacts
    # -------------------
    gan = data["gan"]["gan_checkerboard_artifacts"]

    if gan["mean_checker_peaks"] > 10:
        ai_score += 2
        reasons.append("checkerboard GAN artifacts")

    # -------------------
    # Diffusion artifacts
    # -------------------
    diff = data["gan"]["diffusion_sampling_artifacts"]

    if diff["radial_peak_density"] > 0.35:
        ai_score += 2
        reasons.append("diffusion sampling artifacts")

    # -------------------
    # Frequency statistics
    # -------------------
    freq = data["frequency_domain_analysis"]["frequency_analysis"]

    if freq["spectral_flatness"] > 0.995:
        ai_score += 1
        reasons.append("abnormally flat frequency spectrum")

    # -------------------
    # Perturbation stability
    # -------------------
    pert = data["perturbation"]["perturbation_robustness"]

    if pert["std_similarity"] < 0.001:
        ai_score += 1
        reasons.append("overly stable embedding under perturbations")

    # -------------------
    # Final scoring
    # -------------------
    total = ai_score + real_score

    if total == 0:
        return {
            "mark": "UNCERTAIN",
            "confidence": 0.0,
            "reason": "insufficient forensic signals"
        }

    confidence = max(ai_score, real_score) / total * 100

    if confidence < 0.6:
        mark = "UNCERTAIN"
    elif ai_score > real_score:
        mark = "AI"
    else:
        mark = "NONAI"

    reason = ", ".join(reasons[:2]) if reasons else "mixed forensic signals"

    return {
        "mark": mark,
        "confidence": round(confidence, 2),
        "reason": reason
    }

def process(data):
    result = detect(data)
    # return json.dumps(result, indent=2)
    return result