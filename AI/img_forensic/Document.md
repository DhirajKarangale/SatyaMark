
# Image Forensics Toolkit — Full Documentation

## Overview
A comprehensive system for detecting AI-generated vs real images using multi-stage forensic analysis: watermark detection, sensor fingerprinting, GAN artifacts, metadata verification, semantic consistency, and an LLM decision engine.

## Local Usage Guide
- Run single-image analysis: `python img_forensic.py`
- Run URL-based analysis: use `analyze_image_from_url(url)`
- Run dataset evaluation: `python img_forensic_evaluate.py`

## Architecture
1. **Watermark Detection** – C2PA, SynthID, SDXL tags.
2. **Sensor Fingerprint** – PRNU, CFA, patch correlations.
3. **GAN Artifacts** – Classical + ML-based detection.
4. **Local Manipulation** – ELA, noise residuals, reflection/shadow inconsistencies.
5. **Metadata Analysis** – EXIF validation, camera info.
6. **Semantic Consistency** – Depth, lighting, physics, anatomy, YOLO segmentation.
7. **LLM Decision Engine** – Weighted forensic signals aggregated via an LLM.

## Module Documentation
- **img_forensic_watermark_signature.py** – Extracts embedded watermarks.
- **img_forensic_sensor_fingerprint.py** – PRNU-based camera verification.
- **img_forensic_gan_artifacts.py** – Classical GAN artifact metrics.
- **img_forensic_gan_artifacts_ml.py** – Advanced ML GAN artifact detection.
- **img_forensic_local_manipulation.py** – Detects local edits/splicing.
- **img_forensic_metadata.py** – Reads & validates EXIF.
- **img_forensic_semantic_consistency.py** – High-level semantic analysis.
- **img_forensic_forensic_decision.py** – Final classifier using LLM.
- **img_forensic_url_image_checker.py** – Secure URL → image pipeline.
- **img_forensic_evaluate.py** – Batch scoring.

## Dataset Structure
```
/dataset
    /train
    /test
        /ai
        /real
```

## Final Notes
This system combines classical forensics + ML + multimodal reasoning to maximize reliability in AI image detection.
