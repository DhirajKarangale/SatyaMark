def decide_image(
    watermark: dict,
    sensor: dict,
    gan: dict,
    manip: dict,
    meta: dict,
    semantic: dict,
):
    evidence = {}
    ai_votes = 0
    confidence = 0.0

    # -------------------------------------------------
    # 1. WATERMARK (ABSOLUTE SIGNAL)
    # -------------------------------------------------
    wm = watermark.get("watermark_signature", {})
    if wm.get("matched", False):
        evidence["watermark_signature"] = (
            "An embedded AI generation watermark or signature was detected."
        )
        return "AI", 0.95, evidence  # immediate decision

    # -------------------------------------------------
    # 2. SENSOR FINGERPRINT (ONLY IF STRONG)
    # -------------------------------------------------
    sensor_d = sensor.get("sensor_fingerprint", {}).get("details", {})
    patch_corr = sensor_d.get("patch_correlation_avg", None)

    if patch_corr is not None:
        if patch_corr < 0.01:
            ai_votes += 1
            confidence += 0.35
            evidence["sensor_fingerprint"] = (
                "The image lacks natural camera sensor noise patterns, "
                "which strongly suggests it was not captured by a real camera."
            )
        elif patch_corr > 0.08:
            confidence -= 0.20
            evidence["sensor_fingerprint"] = (
                "Strong camera sensor noise patterns were detected, "
                "which is typical of real photographs."
            )
        else:
            evidence["sensor_fingerprint"] = (
                "Camera sensor patterns are inconclusive."
            )

    # -------------------------------------------------
    # 3. METADATA (SUPPORTING ONLY)
    # -------------------------------------------------
    exif = meta.get("exif_analysis", {})
    has_exif = exif.get("has_exif", False)

    if has_exif:
        confidence -= 0.10
        evidence["metadata"] = (
            "Camera metadata is present, supporting that the image is a real photograph."
        )
    else:
        evidence["metadata"] = (
            "Camera metadata is missing, which is common for both AI-generated "
            "and online-shared real images."
        )

    # -------------------------------------------------
    # 4. SEMANTIC CONSISTENCY (VERY LIGHT)
    # -------------------------------------------------
    sem_score = semantic.get("semantic_consistency", {}).get("consistency_score", None)

    if sem_score is not None:
        if sem_score < 0.35:
            ai_votes += 1
            confidence += 0.15
            evidence["semantic_consistency"] = (
                "The image shows subtle inconsistencies in lighting, depth, or structure."
            )
        else:
            evidence["semantic_consistency"] = (
                "The scene structure appears visually consistent."
            )

    # -------------------------------------------------
    # 5. GAN ARTIFACTS (HINT ONLY)
    # -------------------------------------------------
    gan_score = gan.get("gan_artifacts", {}).get("artifact_score", None)

    if gan_score is not None and gan_score > 0.7:
        ai_votes += 1
        confidence += 0.10
        evidence["gan_artifacts"] = (
            "Subtle texture patterns commonly associated with AI image generation were detected."
        )

    # -------------------------------------------------
    # FINAL DECISION (VOTING + CONFIDENCE)
    # -------------------------------------------------
    confidence = min(max(confidence, 0.0), 1.0)

    if ai_votes >= 2 and confidence >= 0.45:
        return "AI", round(confidence, 2), evidence

    if confidence <= 0.20:
        return "NONAI", round(1 - confidence, 2), evidence

    return "INSUFFICIENT", round(0.5, 2), evidence
