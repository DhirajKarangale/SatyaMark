def build_reason(mark: str, evidence: dict):
    if mark == "AI":
        return (
            "After analyzing the image using multiple forensic checks, the image is "
            "most likely generated or enhanced using artificial intelligence. "
            + " ".join(evidence.values())
        )

    if mark == "NONAI":
        return (
            "The image shows characteristics commonly found in real photographs, "
            "including natural camera patterns and realistic visual structure."
        )

    return (
        "The available forensic evidence is mixed or inconclusive, making it difficult "
        "to reliably determine whether the image is real or AI-generated."
    )
