def rule_based_decision(w, s, g, l, m, sc):
    ai_votes = 0
    confidence = 0.0
    signals = {}
    evidence = {}

    # ---------- WATERMARK (ABSOLUTE) ----------
    wm = w.get("watermark_signature", {})
    if wm.get("matched"):
        return {
            "status": "AI",
            "confidence": 0.95,
            "signals": {"watermark": True},
            "evidence": {
                "watermark": "An embedded AI generation watermark was detected."
            },
        }

    # ---------- SENSOR ----------
    patch_corr = (
        s.get("sensor_fingerprint", {})
        .get("details", {})
        .get("patch_correlation_avg")
    )

    if patch_corr is not None:
        signals["sensor_patch_corr"] = round(patch_corr, 4)

        if patch_corr < 0.01:
            ai_votes += 1
            confidence += 0.35
            evidence["sensor"] = (
                "Natural camera sensor noise patterns are missing or extremely weak."
            )
        elif patch_corr > 0.08:
            confidence -= 0.25
            evidence["sensor"] = (
                "Strong natural camera sensor noise patterns detected."
            )

    # ---------- METADATA (WEAK) ----------
    has_exif = m.get("exif_analysis", {}).get("has_exif", False)
    signals["has_exif"] = has_exif

    if has_exif:
        confidence -= 0.10
        evidence["metadata"] = (
            "Camera metadata is present, supporting a real photograph."
        )
    else:
        evidence["metadata"] = (
            "Camera metadata is missing, which is common for both AI images "
            "and online-shared real photos."
        )

    # ---------- SEMANTIC (LIGHT) ----------
    sem_score = sc.get("semantic_consistency", {}).get("consistency_score")
    if sem_score is not None:
        signals["semantic_score"] = round(sem_score, 2)

        if sem_score < 0.35:
            ai_votes += 1
            confidence += 0.15
            evidence["semantic"] = (
                "Visual inconsistencies detected in lighting, depth, or structure."
            )

    # ---------- GAN ARTIFACTS (VERY WEAK) ----------
    gan_score = g.get("gan_artifacts", {}).get("artifact_score")
    if gan_score is not None:
        signals["gan_score"] = round(gan_score, 2)

        if gan_score > 0.7:
            ai_votes += 1
            confidence += 0.10
            evidence["gan"] = (
                "Subtle texture patterns associated with AI image generation detected."
            )

    confidence = min(max(confidence, 0.0), 1.0)

    # ---------- DECISION ----------
    if ai_votes >= 2 and confidence >= 0.45:
        return {
            "status": "AI",
            "confidence": round(confidence, 2),
            "signals": signals,
            "evidence": evidence,
        }

    if confidence <= 0.20:
        return {
            "status": "NONAI",
            "confidence": round(1 - confidence, 2),
            "signals": signals,
            "evidence": evidence,
        }

    return {
        "status": "UNCERTAIN",
        "confidence": round(0.5, 2),
        "signals": signals,
        "evidence": evidence,
    }
