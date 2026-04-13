import human_translator

def detect(data):
    ai_score = 0
    real_score = 0
    reasons = []

    # -------------------
    # Existing Forensic Checks (Metadata, C2PA, SPN, GAN, etc.)
    # -------------------
    meta = data.get("metadata", {}).get("analysis", {})
    if meta.get("has_exif") and meta.get("camera_valid"):
        real_score += 2
    else:
        ai_score += 1
        reasons.append("missing camera metadata")

    c2pa_data = data.get("c2pa", {})
    if c2pa_data.get("c2pa_present") and c2pa_data.get("valid_signature"):
        real_score += 5
        reasons.append("verified provenance signature")

    spn = data.get("sensor_pattern_noise", {}).get("spn_metrics", {})
    if spn.get("horizontal_correlation", 0) > 0.75 and spn.get("vertical_correlation", 0) > 0.75:
        real_score += 3
    else:
        ai_score += 2
        reasons.append("weak sensor noise pattern")

    gan = data.get("gan", {}).get("gan_checkerboard_artifacts", {})
    if gan.get("mean_checker_peaks", 0) > 10:
        ai_score += 2
        reasons.append("checkerboard GAN artifacts")

    diff = data.get("gan", {}).get("diffusion_sampling_artifacts", {})
    if diff.get("radial_peak_density", 0) > 0.35:
        ai_score += 2
        reasons.append("diffusion sampling artifacts")

    # -------------------
    # Physics & Geometry
    # -------------------
    physics = data.get("physics_geometry", {}).get("physics_and_geometry", {})
    illumination = physics.get("illumination", {})
    perspective = physics.get("perspective", {})
    
    if illumination.get("lighting_consistency_score", 0) > 0.9:
        real_score += 2
    elif illumination.get("lighting_angle_variance", 0) > 1.2:
        ai_score += 2
        reasons.append("inconsistent lighting geometry")

    # -------------------
    # ELA (Error Level Analysis)
    # -------------------
    ela = data.get("ela_analysis", {})
    if ela.get("is_suspicious"):
        ai_score += 3
        reasons.append("inconsistent compression levels")
    else:
        real_score += 1

    # -------------------
    # Autoencoder Reconstruction
    # -------------------
    ae = data.get("autoencoder_reconstruction", {})
    if ae.get("is_suspiciously_simple"):
        ai_score += 3
        reasons.append("low latent complexity")
    else:
        real_score += 2

    # -------------------
    # Diffusion Latent Analysis
    # -------------------
    latent = data.get("diffusion_latent_analysis", {})
    if latent.get("is_diffusion_aligned"):
        ai_score += 4
        reasons.append("Gaussian noise alignment (Diffusion)")
    elif latent.get("latent_kurtosis", 0) > 50:
        real_score += 3
        reasons.append("natural high-kurtosis noise")

    # -------------------
    # NEW: Benford's Law Analysis
    # -------------------
    benford = data.get("benfords_law", {})
    if "benford_chi_square" in benford:
        chi_val = benford.get("benford_chi_square", 1.0)
        if chi_val < 0.05:
            real_score += 3
        elif chi_val > 0.15:
            ai_score += 3
            reasons.append("unnatural Benford's Law statistical distribution")

    # -------------------
    # NEW: Chromatic Aberration
    # -------------------
    ca = data.get("chromatic_aberration", {})
    if ca.get("has_natural_lens_dispersion"):
        real_score += 3
    elif ca.get("aberration_shift", 1.0) < 0.005:
        ai_score += 2
        reasons.append("unnatural edge-to-edge optical perfection")

    # -------------------
    # NEW: Patch Analysis (Texture Tiling)
    # -------------------
    patch = data.get("patch_analysis", {})
    if patch.get("is_suspicious"):
        ai_score += 2
        reasons.append("suspicious repeating texture patches detected")

    # -------------------
    # NEW: Copy-Move Forgery Detection
    # -------------------
    copy_move_data = data.get("copy_move", {})
    if copy_move_data.get("is_copy_move_detected"):
        ai_score += 3
        matches = copy_move_data.get("patch_matches_found", 0)
        reasons.append(f"copy-move forgery detected ({matches} cloned blocks)")

    # -------------------
    # Frequency & Perturbation
    # -------------------
    freq = data.get("frequency_domain_analysis", {}).get("frequency_analysis", {})
    if freq.get("spectral_flatness", 0) > 0.995:
        ai_score += 1
        reasons.append("flat frequency spectrum")

    pert = data.get("perturbation", {}).get("perturbation_robustness", {})
    if pert.get("std_similarity", 1) < 0.001:
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

    human_friendly_reason = human_translator.translate_forensics(
        mark=mark, 
        confidence=round(confidence, 2), 
        ai_score=ai_score, 
        real_score=real_score, 
        all_reasons=reasons, 
        raw_data=data 
    )

    return {
        "mark": mark,
        "confidence": round(confidence, 2),
        "reason": human_friendly_reason,
    }

def process(data):
    return detect(data)