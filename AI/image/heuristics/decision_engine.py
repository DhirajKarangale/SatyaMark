import os
from . import human_translator
from .feature_extractor import extract_feature_vector

ML_MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "classifier.joblib")
classifier = None
try:
    if os.path.exists(ML_MODEL_PATH):
        from joblib import load
        classifier = load(ML_MODEL_PATH)
except Exception as e:
    import logging
    logging.getLogger(__name__).warning(f"Failed to load ML classifier: {e}")

def detect(data):
    ai_score = 0
    real_score = 0
    reasons = []


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


    physics = data.get("physics_geometry", {}).get("physics_and_geometry", {})
    illumination = physics.get("illumination", {})
    perspective = physics.get("perspective", {})
    
    if illumination.get("lighting_consistency_score", 0) > 0.9:
        real_score += 2
    elif illumination.get("lighting_angle_variance", 0) > 1.2:
        ai_score += 2
        reasons.append("inconsistent lighting geometry")


    ela = data.get("ela_analysis", {})
    if ela.get("is_suspicious"):
        ai_score += 3
        reasons.append("inconsistent compression levels")
    else:
        real_score += 1


    ae = data.get("autoencoder_reconstruction", {})
    if ae.get("is_suspiciously_simple"):
        ai_score += 3
        reasons.append("low latent complexity")
    else:
        real_score += 2


    latent = data.get("diffusion_latent_analysis", {})
    if latent.get("is_diffusion_aligned"):
        ai_score += 4
        reasons.append("Gaussian noise alignment (Diffusion)")
    elif latent.get("latent_kurtosis", 0) > 50:
        real_score += 3
        reasons.append("natural high-kurtosis noise")


    benford = data.get("benfords_law", {})
    if "benford_chi_square" in benford:
        chi_val = benford.get("benford_chi_square", 1.0)
        if chi_val < 0.05:
            real_score += 3
        elif chi_val > 0.15:
            ai_score += 3
            reasons.append("unnatural Benford's Law statistical distribution")


    ca = data.get("chromatic_aberration", {})
    if ca.get("has_natural_lens_dispersion"):
        real_score += 3
    elif ca.get("aberration_shift", 1.0) < 0.005:
        ai_score += 2
        reasons.append("unnatural edge-to-edge optical perfection")


    patch = data.get("patch_analysis", {})
    if patch.get("is_suspicious"):
        ai_score += 2
        reasons.append("suspicious repeating texture patches detected")


    copy_move_data = data.get("copy_move", {})
    if copy_move_data.get("is_copy_move_detected"):
        ai_score += 3
        matches = copy_move_data.get("patch_matches_found", 0)
        reasons.append(f"copy-move forgery detected ({matches} cloned blocks)")


    freq = data.get("frequency_domain_analysis", {}).get("frequency_analysis", {})
    if freq.get("spectral_flatness", 0) > 0.995:
        ai_score += 1
        reasons.append("flat frequency spectrum")

    pert = data.get("perturbation", {}).get("perturbation_robustness", {})
    if pert.get("std_similarity", 1) < 0.001:
        ai_score += 1
        reasons.append("overly stable perturbation embedding")

    # ---- Watermark Analysis (previously unused) ----
    wm = data.get("watermark", {}).get("watermark_analysis", {})
    if wm.get("watermark_detected"):
        ai_score += 2
        reasons.append("periodic watermark pattern detected")
    elif wm.get("watermark_score", 0) > 10:
        ai_score += 1
        reasons.append("elevated watermark-like signal")

    # ---- Visual Artifact Analysis (previously unused) ----
    visual = data.get("visual", {}).get("visual_artifact_features", {})
    if visual:
        noise_feat = visual.get("noise", {})
        sym_feat = visual.get("symmetry", {})
        tex_feat = visual.get("texture_blocks", {})

        if noise_feat.get("residual_variance", 999) < 1.0:
            ai_score += 2
            reasons.append("unnaturally low noise residual variance")

        if sym_feat.get("symmetry_score", 0) > 0.95:
            ai_score += 1
            reasons.append("unnaturally perfect bilateral symmetry")

        if tex_feat.get("block_variance_global", 999) < 50:
            ai_score += 1
            reasons.append("unnaturally uniform texture blocks")

    # ---- Compression Artifact Analysis (previously unused) ----
    comp = data.get("compression_artifact_analysis", {}).get("compression_analysis", {})
    if comp:
        if comp.get("double_jpeg_probability", 0) > 0.3:
            ai_score += 2
            reasons.append("double JPEG compression detected (likely re-saved or tampered)")

        if comp.get("dct_zero_ratio", 0) > 0.7:
            ai_score += 1
            reasons.append("high DCT zero coefficient ratio")

    # ---- Pixel Level Analysis (previously unused) ----
    pixel = data.get("pixel", {})
    if pixel:
        kurt = pixel.get("kurtosis", {})
        if kurt:
            avg_kurtosis = (kurt.get("r", 5) + kurt.get("g", 5) + kurt.get("b", 5)) / 3
            if avg_kurtosis < 1.0:
                ai_score += 2
                reasons.append("unnaturally low channel kurtosis (AI-smooth pixel distribution)")
            elif avg_kurtosis > 8.0:
                real_score += 2

        neighbor = pixel.get("neighbor_correlation", {})
        if neighbor:
            h_corr = neighbor.get("horizontal", 0)
            v_corr = neighbor.get("vertical", 0)
            if h_corr > 0.995 and v_corr > 0.995:
                ai_score += 1
                reasons.append("suspiciously high pixel neighbor correlation")

        res_noise = pixel.get("residual_noise", {})
        if res_noise:
            if res_noise.get("kurtosis", 5) < 0.5:
                ai_score += 1
                reasons.append("low residual noise kurtosis (too clean)")
            elif res_noise.get("kurtosis", 0) > 10:
                real_score += 1


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
        
    # ML Classifier Override
    if classifier is not None:
        try:
            vec = extract_feature_vector(data)
            probs = classifier.predict_proba([vec])[0]
            pred_class = classifier.classes_[probs.argmax()]
            max_prob = max(probs)
            
            if max_prob >= 0.65:
                mark = "AI" if pred_class == 1 else "NONAI"
                confidence = max_prob * 100
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"ML override failed, falling back to rules: {e}")

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