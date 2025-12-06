# Image Verification Using HuggingFace Models

## Overview
This module detects whether an image is **AI-generated or real** using a **multi-model ensemble** built entirely on local HuggingFace models and lightweight forensic tools.  
Each model contributes a complementary signal (semantic, forensic, metadata, or embedding); a trained **fusion classifier** merges these signals into a single, explainable AI-likelihood score.

---

## How We Are Doing It (Pipeline)
1. **Load models & preprocess image**  
   - Image is loaded and normalized (resize, center-crop, convert color space) using `utils/image_io.py`.  
2. **Per-model inference**  
   - Each model in `inference/` computes its specific output (embedding, probability, anomaly map, metadata features).  
3. **Forensic feature extraction**  
   - `forensics/` computes ELA, compression patterns, EXIF integrity and other heuristics.  
4. **Feature assembly**  
   - Per-model scalar outputs and forensic values are collected into a single feature vector.  
5. **Fusion classifier**  
   - The fusion classifier (loaded from `models/saved_models/`) consumes the feature vector and returns a final probability and label.  
6. **Result & reasoning**  
   - JSON output includes per-model scores, detected anomalies, and final decision with confidence.

---

## Architecture
```
img_ml/
│
├── inference/
│   ├── clip_models.py       # CLIP H/14 & CLIP bigG inference & prompt scoring
│   ├── dino.py              # DINOv2 embeddings + SVM wrapper
│   ├── fatformer.py         # FatFormer AI-probability scorer
│   ├── ghostnet.py          # GhostNet forensic anomaly scoring
│   ├── mantranet.py         # MantraNet local anomaly / tamper heatmap
│   ├── detector.py          # Master aggregator calling all model wrappers
│   └── utils.py             # Preprocessing helpers for all models
│
├── forensics/
│   ├── ela.py               # Error Level Analysis helpers
│   └── forensic_features.py # EXIF extraction, compression & image stats
│
├── fusion/
│   ├── train_fusion.py      # Train the meta-model (fusion classifier)
│   ├── meta_model.py        # Fusion model definition & feature schema
│
├── models/
│   ├── loaders.py           # Standardized HuggingFace model loading utilities
│   ├── model_wrappers.py    # Per-model inference wrappers that return scalars
│   └── saved_models/        # Trained SVM & fusion joblib/pickle files
│
├── scripts/
│   ├── make_dataset_csv.py  # Build dataset.csv from folders and labels
│   ├── clean_dataset.py     # Validate and remove broken images / duplicates
│
├── utils/
│   ├── device.py            # Detect CUDA/CPU and recommended device
│   ├── image_io.py          # Image read/resize/normalize routines
│   └── persistence.py       # Save/load helpers for models and artifacts
│
└── img_ml_verify.py         # Entry point: image -> JSON result
```

---

## Role of Each Model — Detailed

### 1) **DINOv2 (Embeddings → SVM)**
- **What it produces:** A fixed-length embedding vector representing high-level visual features.  
- **How it's used:** An SVM (or small classifier) is trained on labeled embeddings to produce `dino_prob` (0–1).  
- **Why it helps:** Embeddings capture global scene/layout/texture patterns. AI-generated images often lie in distributional pockets separable in embedding space.  
- **Failure modes:** Very stylized or highly post-processed real photos may drift; embeddings are sensitive to strong augmentations.

### 2) **FatFormer (Direct AI classifier)**
- **What it produces:** Direct binary probability of being AI-produced.  
- **How it's used:** Fine-tuned on labeled real vs synthetic images; returns `fatformer_prob`.  
- **Why it helps:** Specialized network trained on generative model artifacts (blur patterns, upsampling artifacts, synthesis fingerprints).  
- **Failure modes:** Can be overconfident on unseen generative architectures; retrain when new generators emerge.

### 3) **GhostNet Forensics (Forensic Anomaly Score)**
- **What it produces:** A low-level anomaly score based on atypical noise/textural statistics.  
- **How it's used:** Computes `ghostnet_score` that quantifies micro-texture inconsistency relative to natural camera noise.  
- **Why it helps:** Detects diffusion/gan textures and synthetic smoothing not visible to semantic models.  
- **Failure modes:** Heavy denoising, aggressive compression, or photo-editing can look anomalous.

### 4) **CLIP H/14 & CLIP bigG (Prompt-based Semantic Scoring)**
- **What they produce:** Similarity scores between the image and textual prompts like “a photo taken with a camera” vs “a digital artwork / generated image.”  
- **How they're used:** Convert similarity differences to `clip_h14_prob` and `clip_bigg_prob`. Use multiple prompts for robustness (e.g., “real photo”, “photograph”, “rendered image”).  
- **Why they help:** Catch semantic inconsistencies — impossible shadows, unnatural hands, odd object geometry — that look wrong to language-conditioned vision models.  
- **Failure modes:** Strong domain-shift (e.g., macro photography, medical imaging) where natural photos don’t match generic prompts.

### 5) **MantraNet (Local Tampering / Heatmap)**
- **What it produces:** Pixel- or patch-level anomaly heatmap and aggregated `mantra_anomaly` score.  
- **How it's used:** Local inconsistencies (splices, cloned regions, patch-blending) are summarized into a scalar used by the fusion model.  
- **Why it helps:** Detects partial synthesis, splices, or inpainting which a global classifier might miss.  
- **Failure modes:** Global synthetic images (whole-image generation) show low localized anomaly even if synthetic overall.

### 6) **EXIF / Light Forensics**
- **What it produces:** Structured metadata features: presence/absence of EXIF, camera model plausibility, software tags (e.g., Adobe, Photoshop), GPS anomalies, compression chain indicators.  
- **How it's used:** Simple rule-based or ML-encoded features (`exif_score`, `has_exif`, `software_flag`).  
- **Why it helps:** Many synthetic images lack camera EXIF or include known generator software traces.  
- **Failure modes:** Metadata can be stripped or intentionally forged; absence of EXIF is not proof of synthesis.

### 7) **Fusion Classifier (Meta-model)**
- **What it produces:** Final probability `fusion_prob` and class label (AI / NON-AI).  
- **How it's used:** Trained on the concatenated per-model features (see feature-schema below) using logistic regression / XGBoost / small MLP.  
- **Why it helps:** Combines orthogonal signals; reduces single-model overfitting; increases robustness.  
- **Failure modes:** Garbage-in → garbage-out. Fusion quality depends on diverse training data that represents expected real-world inputs.

---

## Feature Schema (example)
A typical feature vector passed to fusion might include:
```
[
  dino_prob,
  fatformer_prob,
  ghostnet_score,
  clip_h14_prob,
  clip_bigg_prob,
  mantra_anomaly,
  exif_score,
  image_entropy,
  compression_level
]
```
All features must be scaled/normalized the same way used during training (see `fusion/meta_model.py` and `train_fusion.py`).

---

## How We Reach the Result (Inference Walkthrough)

1. `img_ml_verify.py` accepts a path or URL. It validates and downloads image if needed.
2. Preprocess (resize, normalize) using `utils/image_io.py`.
3. For each model wrapper in `inference/`:
   - Run model-specific preprocessing.
   - Obtain scalar outputs or small arrays (heatmaps).
   - Post-process into scalar features (e.g., aggregate heatmap → mean anomaly).
4. Run forensic scripts in `forensics/` to produce metadata + ELA signals.
5. Assemble the feature vector and apply the same scaling pipeline used during training.
6. Load fusion classifier from `models/saved_models/fusion_model.joblib`.
7. Compute `fusion_prob`. Apply configured threshold (e.g., 0.5 default) to produce label:
   - `fusion_prob >= 0.5` → **AI**
   - `fusion_prob < 0.5` → **NON-AI**
8. Output JSON:
```json
{
  "dino_prob": 0.32,
  "fatformer_prob": 0.88,
  "ghostnet_score": 0.12,
  "clip_h14_prob": 0.75,
  "mantra_anomaly": 0.05,
  "exif_score": 0.0,
  "fusion_prob": 0.82,
  "label": "AI",
  "reasoning": [
     "FatFormer strongly indicates AI",
     "CLIP semantic mismatch",
     "EXIF missing"
  ]
}
```
9. Optionally, save per-run debug artifacts (heatmaps, intermediate tensors) for inspection.

---

## Instructions — Device Check, Dataset, Clean, Train

> **📌 Important:**  
> 1. **Activate your virtual environment (`venv`) first.**  
> 2. Then run **all commands from the root of the `SatyaMark` directory**, for example:
> ```
> SatyaMark/     ← run commands here after venv activation
> └── AI/
>     └── img_ml/
> ```

---

### 1) Check Device (GPU)
Use the provided utility:
```bash
python -c "from img_ml.utils.device import get_device; print(get_device())"
```
Or manually:
```bash
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```
If using Nvidia GPU, install correct CUDA wheel:
```bash
pip install --index-url https://download.pytorch.org/whl/cu121 torch torchvision --upgrade
```

### 2) Build / Clean Dataset
- **Create CSV of dataset** (labels folder-based):
```bash
python -m AI.img_ml.scripts.make_dataset_csv 
```
- **Clean dataset (remove corrupt / tiny images)**:
```bash
python -m AI.img_ml.scripts.clean_dataset 
```
- Confirm `dataset.csv` exists and contains columns: `filepath,label,split`.

### 3) Train Fusion Classifier
```bash
python -m AI.img_ml.fusion.train_fusion 
```
- `train_fusion.py` will:
  - Load per-image features (or compute them on-the-fly)
  - Apply scaler / normalization
  - Train the selected model (logistic / xgboost / mlp)
  - Save model and scaler to `models/saved_models/`

---

## Troubleshooting & Tips
- **Low fusion accuracy** → check class balance in `dataset.csv`, augment with diverse real photos and multiple generator outputs.
- **Model OOM on GPU** → reduce batch size or run per-model inference on CPU for large models.
- **Missing EXIF** → not necessarily AI; strip/preserve metadata culture differs by pipeline.
- **New generative models** → retrain FatFormer and update dataset with outputs from the newest generators.
- **Calibration** → tune decision threshold on validation set for precision/recall balance.

---

## Improving System
- Add more specialized detectors for faces, hands, or fonts.
- Use ensembling at fusion level (stacked models) and calibrated probabilities.
- Maintain a rolling dataset of recent generator outputs for continual learning.

---

## Final Note
This repository provides a practical, modular pipeline to detect synthetic images by merging orthogonal signals. It's designed for offline use, explainability, and easy extensibility. Keep datasets fresh and retrain periodically as synthetic image quality evolves.

---
