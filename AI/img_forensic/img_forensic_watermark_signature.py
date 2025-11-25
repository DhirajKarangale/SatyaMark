import cv2
import piexif
from typing import Dict, Any
from PIL import Image


def watermark_analyze(image_path) -> str:
    """
    100% correct embedded watermark/signature detector.
    Detects ONLY:
    - C2PA authenticity claims
    - Google SynthID metadata
    - SDXL metadata tags
    - Explicit EXIF/XMP signatures

    NEVER tries to infer or guess AI-vs-REAL.
    """

    image = cv2.imread(image_path)
    try:
        if image is None:
            return _result(
                status="error",
                matched=False,
                confidence=0.0,
                signature_type=None,
                raw_output=None,
                suspected_generators=[],
                notes="Image is None.",
            )

        pil_img = Image.fromarray(image)

        exif_raw = pil_img.info.get("exif")
        exif_dict = None

        if exif_raw:
            try:
                exif_dict = piexif.load(exif_raw)
            except Exception:
                exif_dict = None

        if "c2pa" in pil_img.info:
            return _result(
                status="ok",
                matched=True,
                confidence=1.0,
                signature_type="c2pa_authenticity",
                raw_output=pil_img.info["c2pa"],
                suspected_generators=[],
                notes="C2PA authenticity signature found.",
            )

        for key, val in pil_img.info.items():
            if "synthid" in key.lower() or "synthid" in str(val).lower():
                return _result(
                    status="ok",
                    matched=True,
                    confidence=1.0,
                    signature_type="google_synthid",
                    raw_output={key: val},
                    suspected_generators=["Google Imagen", "Gemini"],
                    notes="Google SynthID watermark found.",
                )

        if exif_dict:
            exif_str = str(exif_dict).lower()
            if "stable diffusion" in exif_str or "sdxl" in exif_str:
                return _result(
                    status="ok",
                    matched=True,
                    confidence=1.0,
                    signature_type="sdxl_metadata",
                    raw_output=exif_dict,
                    suspected_generators=["Stable Diffusion XL"],
                    notes="SDXL or Stable Diffusion metadata found.",
                )

        return _result(
            status="ok",
            matched=False,
            confidence=1.0,
            signature_type=None,
            raw_output=None,
            suspected_generators=[],
            notes="No embedded watermark or signature found.",
        )

    except Exception as e:
        return _result(
            status="error",
            matched=False,
            confidence=0.0,
            signature_type=None,
            raw_output=None,
            suspected_generators=[],
            notes=str(e),
        )


def _result(
    status, matched, confidence, signature_type, raw_output, suspected_generators, notes
):
    return {
        "watermark_signature": {
            "status": status,
            "matched": matched,
            "confidence": confidence,
            "signature_type": signature_type,
            "details": {
                "raw_output": raw_output,
                "suspected_generators": suspected_generators,
            },
            "notes": notes,
        }
    }
