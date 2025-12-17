def build_reason(mark: str, evidence: dict):
    if mark == "AI":
        reason = (
            "After carefully analyzing the image using multiple visual and forensic checks, "
            "the image is most likely generated or significantly altered using artificial intelligence. "
        )

        if "sensor_fingerprint" in evidence:
            reason += (
                "Real photographs captured by cameras usually contain subtle, natural noise patterns "
                "introduced by camera sensors. In this image, those natural sensor patterns are missing "
                "or unusually weak, which strongly suggests the image was not captured by a physical camera. "
            )

        if "metadata" in evidence:
            reason += (
                "Additionally, real photos typically store camera information such as device model, "
                "lens details, or capture settings. This image does not contain such information, "
                "which is commonly observed in AI-generated or heavily processed images. "
            )

        if "semantic_consistency" in evidence:
            reason += (
                "While parts of the image may appear visually realistic at first glance, "
                "the overall scene shows subtle inconsistencies in lighting, depth, or structure "
                "that do not fully match how real-world scenes are naturally formed or photographed. "
            )

        if "gan_artifacts" in evidence:
            reason += (
                "The image also contains faint texture patterns that are often introduced by "
                "image generation models. These patterns are not usually visible in real photographs "
                "but are a known side effect of AI image synthesis. "
            )

        reason += (
            "When all these signals are considered together, they strongly indicate that the image "
            "was created or enhanced using artificial intelligence rather than captured in the real world."
        )

        return reason

    if mark == "NONAI":
        return (
            "This image shows strong signs of being a real photograph captured by a physical camera. "
            "It contains natural sensor noise patterns that are typical of camera hardware, "
            "along with consistent lighting, depth, and realistic scene structure. "
            "The presence of these characteristics suggests the image was captured in a real environment "
            "and has not been generated or significantly altered by artificial intelligence."
        )

    # INSUFFICIENT
    return (
        "The image was analyzed using multiple forensic and visual checks, but the results were mixed. "
        "Some indicators suggest realism while others are inconclusive or unclear. "
        "Due to these conflicting signals, there is not enough reliable evidence to confidently determine "
        "whether the image is real or AI-generated."
    )


def build_final_result(mark, score, evidence):
    return {
        "mark": mark,
        "confidence": round(score, 2),
        "reason": build_reason(mark, evidence),
    }
