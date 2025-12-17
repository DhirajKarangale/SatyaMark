def decide_image(
    watermark: dict,
    sensor: dict,
    gan: dict,
    manip: dict,
    meta: dict,
    semantic: dict,
):
    score = 0.0
    evidence = {}

    # -------------------------------------------------
    # 1. SENSOR FINGERPRINT (STRONGEST)
    # -------------------------------------------------
    sensor_d = sensor.get("sensor_fingerprint", {}).get("details", {})
    patch_corr = sensor_d.get("patch_correlation_avg", 0.0)

    if patch_corr < 0.02:
        score += 0.35
        evidence["sensor_fingerprint"] = (
            f"Weak sensor fingerprint detected (patch correlation {patch_corr:.4f}), "
            "which is uncommon in real camera images."
        )
    elif patch_corr > 0.08:
        score -= 0.25
        evidence["sensor_fingerprint"] = (
            f"Strong sensor fingerprint detected (patch correlation {patch_corr:.4f}), "
            "consistent with real camera noise."
        )
    else:
        evidence["sensor_fingerprint"] = (
            f"Sensor fingerprint is inconclusive (patch correlation {patch_corr:.4f})."
        )

    # -------------------------------------------------
    # 2. METADATA
    # -------------------------------------------------
    exif = meta.get("exif_analysis", {})
    has_exif = exif.get("has_exif", False)

    if not has_exif:
        score += 0.25
        evidence["metadata"] = (
            "No EXIF metadata found. AI-generated and reprocessed images "
            "commonly lack camera metadata."
        )
    else:
        cam = exif.get("details", {})
        score -= 0.10
        evidence["metadata"] = (
            f"Camera metadata present (Make: {cam.get('camera_make')}, "
            f"Model: {cam.get('camera_model')}), which supports a real image."
        )

    # -------------------------------------------------
    # 3. SEMANTIC CONSISTENCY
    # -------------------------------------------------
    sem = semantic.get("semantic_consistency", {})
    sem_score = sem.get("consistency_score", 0.5)

    if sem_score < 0.45:
        score += 0.20
        evidence["semantic_consistency"] = (
            f"Low semantic consistency score ({sem_score:.2f}), "
            "indicating unrealistic lighting, depth, or object structure."
        )
    elif sem_score > 0.70:
        score -= 0.10
        evidence["semantic_consistency"] = (
            f"High semantic consistency score ({sem_score:.2f}), "
            "suggesting realistic scene structure."
        )
    else:
        evidence["semantic_consistency"] = (
            f"Semantic consistency score ({sem_score:.2f}) is inconclusive."
        )

    # -------------------------------------------------
    # 4. LOCAL MANIPULATION
    # -------------------------------------------------
    lm = manip.get("local_manipulation", {})
    lm_conf = lm.get("confidence", 0.0)

    if lm_conf > 0.35:
        score += 0.10
        evidence["local_manipulation"] = (
            f"Localized manipulation artifacts detected "
            f"(confidence {lm_conf:.2f})."
        )
    else:
        evidence["local_manipulation"] = (
            "No strong localized manipulation patterns detected."
        )

    # -------------------------------------------------
    # 5. WATERMARK / SIGNATURE
    # -------------------------------------------------
    wm = watermark.get("watermark_signature", {})
    if wm.get("matched", False):
        score += 0.40
        evidence["watermark_signature"] = (
            "Embedded AI generation watermark or signature detected."
        )
    else:
        evidence["watermark_signature"] = (
            "No embedded AI watermark or generation signature detected."
        )

    # -------------------------------------------------
    # 6. GAN ARTIFACTS (WEAK SIGNAL)
    # -------------------------------------------------
    gan_score = gan.get("gan_artifacts", {}).get("artifact_score", 0.0)

    if gan_score > 0.5:
        score += 0.05
        evidence["gan_artifacts"] = (
            f"Weak GAN-style texture artifacts detected "
            f"(score {gan_score:.2f})."
        )
    else:
        evidence["gan_artifacts"] = (
            "No strong GAN artifact patterns detected."
        )

    # -------------------------------------------------
    # FINAL DECISION
    # -------------------------------------------------
    score = min(max(score, 0.0), 1.0)

    if score >= 0.60:
        mark = "AI"
    elif score <= 0.35:
        mark = "NONAI"
    else:
        mark = "INSUFFICIENT"

    return mark, score, evidence
