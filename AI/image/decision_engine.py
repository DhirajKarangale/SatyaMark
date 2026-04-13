import json

def detect(data):
    ai_score = 0
    real_score = 0
    reasons = []

    # -------------------
    # Existing Forensic Checks (Metadata, C2PA, SPN, GAN, etc.)
    # -------------------
    meta = data["metadata"]["analysis"]
    if meta["has_exif"] and meta["camera_valid"]:
        real_score += 2
    else:
        ai_score += 1
        reasons.append("missing camera metadata")

    if data["c2pa"]["c2pa_present"] and data["c2pa"]["valid_signature"]:
        real_score += 5
        reasons.append("verified provenance signature")

    spn = data["sensor_pattern_noise"]["spn_metrics"]
    if spn["horizontal_correlation"] > 0.75 and spn["vertical_correlation"] > 0.75:
        real_score += 3
    else:
        ai_score += 2
        reasons.append("weak sensor noise pattern")

    gan = data["gan"]["gan_checkerboard_artifacts"]
    if gan["mean_checker_peaks"] > 10:
        ai_score += 2
        reasons.append("checkerboard GAN artifacts")

    diff = data["gan"]["diffusion_sampling_artifacts"]
    if diff["radial_peak_density"] > 0.35:
        ai_score += 2
        reasons.append("diffusion sampling artifacts")

    # -------------------
    # NEW: Physics & Geometry
    # -------------------
    physics = data["physics_geometry"]["physics_and_geometry"]
    if physics["illumination"]["lighting_consistency_score"] > 0.9:
        real_score += 2
    elif physics["illumination"]["lighting_angle_variance"] > 1.2:
        ai_score += 2
        reasons.append("inconsistent lighting geometry")

    # -------------------
    # NEW: ELA (Error Level Analysis)
    # -------------------
    ela = data["ela_analysis"]
    if ela["is_suspicious"]:
        ai_score += 3
        reasons.append("inconsistent compression levels")
    else:
        real_score += 1

    # -------------------
    # NEW: Autoencoder Reconstruction
    # -------------------
    ae = data["autoencoder_reconstruction"]
    if ae["is_suspiciously_simple"]:
        ai_score += 3
        reasons.append("low latent complexity")
    else:
        real_score += 2

    # -------------------
    # NEW: Diffusion Latent Analysis
    # -------------------
    latent = data["diffusion_latent_analysis"]
    # Real photos have high Kurtosis (spiky noise), AI is Gaussian (Kurtosis ~3)
    if latent["is_diffusion_aligned"]:
        ai_score += 4
        reasons.append("Gaussian noise alignment (Diffusion)")
    elif latent["latent_kurtosis"] > 50:
        real_score += 3
        reasons.append("natural high-kurtosis noise")

    # -------------------
    # Frequency & Perturbation (Existing)
    # -------------------
    freq = data["frequency_domain_analysis"]["frequency_analysis"]
    if freq["spectral_flatness"] > 0.995:
        ai_score += 1
        reasons.append("flat frequency spectrum")

    pert = data["perturbation"]["perturbation_robustness"]
    if pert["std_similarity"] < 0.001:
        ai_score += 1
        reasons.append("overly stable perturbation embedding")

    # -------------------
    # Final scoring
    # -------------------
    total = ai_score + real_score
    if total == 0:
        return {"mark": "UNCERTAIN", "confidence": 0.0, "reason": "insufficient signals"}

    confidence = (max(ai_score, real_score) / total) * 100

    if ai_score > real_score:
        mark = "AI"
    elif real_score > ai_score:
        mark = "NONAI"
    else:
        mark = "UNCERTAIN"

    # Select the top 2 reasons for the verdict
    reason = ", ".join(reasons[:2]) if reasons else "consistent forensic signals"

    return {
        "mark": mark,
        "confidence": round(confidence, 2),
        "reason": reason,
        "signals": {"ai": ai_score, "real": real_score}
    }

def process(data):
    return detect(data)