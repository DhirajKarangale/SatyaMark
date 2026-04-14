# Image Verification Forensic Engine

> **Status:** Active Development — Results may not always be accurate.

---

## Overview
The **Image Verification Forensic Engine** is a multi-stage system that determines whether an image is:

- Real (unaltered photograph)
- AI-generated
- Manipulated / tampered

It combines **cryptography, optical physics, statistical analysis, and AI fingerprint detection** to produce:

- Final classification (AI / NONAI / UNCERTAIN)
- Confidence score (0–100%)
- Human-readable explanation

Unlike black-box detectors, this system relies on **measurable physical and mathematical properties**.

---

## Usage

```python
from main import verify

image_url = "https://example.com/image.png"

result = verify(image_url)
print(result)
```

---

## Processing Pipeline

```
Input Image (URL/File)
        |
        v
[ downloader ]
        |
        v
[ Forensic Modules ]
 ├── metadata
 ├── c2pa
 ├── watermark
 ├── visual_artifacts
 ├── frequency_domain_analysis
 ├── pixel_level_analysis
 ├── sensor_pattern_noise
 ├── compression_artifact_analysis
 ├── gan
 ├── perturbation_robustness_testing
 ├── physics_geometry
 ├── ela_analysis
 ├── autoencoder_reconstruction
 ├── diffusion_latent_analysis
 ├── benfords_law
 ├── chromatic_aberration
 ├── patch_analyzer
 ├── copy_move
        |
        v
[ decision_engine ]
        |
        v
Final Output
```

---

## Module Categories

### 1. Cryptography & Provenance
- metadata (EXIF extraction)
- c2pa (content authenticity)
- watermark (AI watermark detection)

### 2. Optical Physics
- sensor_pattern_noise (camera hardware fingerprint)
- chromatic_aberration (lens distortion)
- physics_geometry (lighting, shadows, perspective)

### 3. Statistical & Frequency Analysis
- benfords_law (pixel distribution validation)
- frequency_domain_analysis (FFT/DCT patterns)
- pixel_level_analysis (pixel anomalies)

### 4. Forgery Detection
- ela_analysis (error level analysis)
- compression_artifact_analysis
- copy_move
- patch_analyzer

### 5. AI Fingerprints
- gan (GAN artifacts)
- diffusion_latent_analysis
- autoencoder_reconstruction
- perturbation_robustness_testing

---

## Decision Engine

All module outputs are aggregated into:

- `ai_score`
- `real_score`

### Logic
- Strong real signals:
  - Valid sensor noise (SPN)
  - Authentic metadata / C2PA

- Strong AI signals:
  - Synthetic noise
  - Missing metadata
  - Physical inconsistencies

### Output
- AI / NONAI / UNCERTAIN
- Confidence score

---

## Output Format

```json
{
  "mark": "AI | NONAI | UNCERTAIN",
  "confidence": 0,
  "reason": "Human-readable explanation",
  "signals": {
    "ai_score": 0,
    "real_score": 0
  }
}
```

---

## Design Principles

- Multi-layer verification
- Physics-based validation
- No single-point failure
- Explainable results
- Modular architecture

---

## Production Notes

Recommended improvement for robustness:

```python
except Exception as e:
    return {
        "mark": "ERROR",
        "confidence": 0,
        "reason": str(e)
    }
```

---

## Disclaimer

This system is under active development.
Results are not guaranteed to be 100% accurate and should not be treated as definitive proof.
