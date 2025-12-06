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

---

# ⚙️ Setup & Usage

Follow these steps to run and test the verification worker locally.

---

## **1. Clone this repository**
```
git clone https://github.com/DhirajKarangale/ai-image-forensic-verify-worker
```

Move into the project directory:
```
cd ai-image-forensic-verify-worker
```

(Or your local machine path:  
`cd C:\SatyaMark\AI\ai-image-forensic-verify-worker`)

---

## **2. Create Virtual Environment (first time only)**
```
python -m venv venv
```

## **3. Activate Virtual Environment**
**Windows:**
```
venv\Scripts\activate
```

**Linux/Mac:**
```
source venv/bin/activate
```

---

## **4. Install Dependencies (first time only)**
```
pip install -r requirements.txt
```

---

## **5. Create `.env` File**

Create `.env` in the project root:

```
HF_TOKEN=your_hf_token_here
REDIS_URL=your_upstash_redis_url_here
```

### Redis uses Streams  
Example:
```
redis://default:password@eu2-magic-redis.upstash.io:12345
```

---

## **6. Run Local Test**
```
python .\local_test.py
```

This will:
- Connect all LLMs  
- Prompt for your test input  
- Run the entire summarization → fact-check → web verification pipeline  
- Print results in terminal  

---

## **7. When Prompted: Enter Environment URL**
`local_test.py` may ask:

```
Enter environment URL:
```

Provide your Upstash Redis URL if required.

---

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

---

### **Note**
*Not 100% accurate. Honestly, nothing I build ever is. Good thing you have a real brain to verify stuff.*

---