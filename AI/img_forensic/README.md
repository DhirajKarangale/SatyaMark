# Image Verification Using Forensics Methods 

## Overview
This system verifies whether an image is **AI-generated or real** by combining multiple forensic signals. Unlike single-model detectors, it evaluates camera noise, metadata, GAN fingerprints, semantic realism, and editing traces, then merges all results using a weighted LLM-based decision model.

## How It Works
1. **Image Validation**  
   Ensures the input (path or URL) is a valid, readable image.

2. **Forensic Analysis (6 Layers)**
   - **Watermark / Signature Detection**  
     Searches for C2PA, SynthID, SDXL, or other embedded AI identifiers.
   - **Sensor Fingerprint (PRNU/CFA)**  
     Extracts camera hardware noise patterns. Real cameras have strong PRNU; AI does not.
   - **GAN Artifact Detection**  
     Classical FFT-based checks + ML-based artifact models (FatFormer, MantraNet, NoisePrint).
   - **Local Manipulation Detection**  
     Uses ELA, noise residue, shadow/reflection mismatch, and region inconsistency.
   - **Metadata / EXIF Analysis**  
     Reads camera model, timestamp, GPS, and software tags. AI images often lack valid EXIF.
   - **Semantic & Physical Consistency**  
     Checks depth, lighting, pose, reflections, object physics, and material realism.

3. **Signal Summarization**  
   Extracted forensic values are compressed into meaningful numeric and boolean indicators.

4. **LLM-Based Reasoning**  
   A lightweight LLM evaluates signals using fixed weights:
   ```
   Sensor: 35%
   Metadata: 25%
   Semantic: 20%
   Manipulation: 10%
   Watermark: 7%
   GAN: 3%
   ```
   Produces:
   ```json
   { "mark": "AI", "reason": "...", "confidence": 0.0–1.0 }
   ```

## Architecture
```
Input Image (path or URL)
        │
        ▼
 Six Forensic Modules
        │
        ▼
LLM Weighted Decision Engine
        │
        ▼
 Final Classification (AI / NONAI)
```

## Module Roles
- **Watermark Signature**  
  Detects built‑in AI or authenticity metadata.

- **Sensor Fingerprint**  
  Measures camera PRNU noise, CFA patterns, and patch correlations.

- **GAN Artifacts**  
  Finds frequency anomalies, texture repetition, and diffusion patterns.

- **Local Manipulation**  
  Identifies tampering: pasted regions, ELA spikes, shadow mismatch.

- **Metadata**  
  Validates EXIF: camera details, timestamps, software history.

- **Semantic Consistency**  
  Tests lighting, depth, anatomy, reflections, and object physics.

- **Decision Engine**  
  Merges all signals into a single consistent result.

## Final Notes
This multi-layer forensic system provides **robust and explainable image verification**.  
Each module contributes a different dimension of evidence, and the weighted LLM ensures reliable final classification.
