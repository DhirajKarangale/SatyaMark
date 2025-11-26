# SatyaMark — Multi-Modal Verification System

SatyaMark is an extensible AI framework designed for **Text Fact Verification**, **AI Image Detection (ML-based)**, and **Image Forensics Verification**.  
It brings together multiple detection pipelines, unified LLM connectors, and modular architecture for scalable, accurate verification across modalities.

---

# 📚 Verification Modules

Below are the three major verification systems included in SatyaMark, each with its own documentation.

---

## [📝 **Text Verification System (LLM-Driven Fact Checking)**](https://github.com/DhirajKarangale/SatyaMark/blob/dev/AI/text/Text_Verification.md)

This pipeline evaluates statements for:
- **Correct**
- **Incorrect**
- **Subjective**
- **Insufficient**

Uses an LLM-driven multi-stage pipeline:
1. Subjectivity check  
2. Claim extraction  
3. Initial correctness scoring  
4. If low confidence → **web search**  
5. Final correctness verdict with explanation  

---

## [🖼️ **Image Verification Using HuggingFace Models (ML-Based Ensemble)**](https://github.com/DhirajKarangale/SatyaMark/blob/dev/AI/img_ml/Image_ML_Verification.md)

This module detects whether an image is **AI-generated or real** using:
- CLIP/Transformers semantic similarity  
- Embedding-based signals  
- Forensic-light cues  
- Metadata features  
- A trained **fusion classifier** (Logistic / LightGBM / etc.)  

---

## [🔍 **Image Verification Using Forensic Signals (Advanced Forensics)**](https://github.com/DhirajKarangale/SatyaMark/blob/dev/AI/img_forensic/Image_Forensic_Verification.md)

Performs deep forensic analysis using:
- **ELA (Error Level Analysis)**  
- **Camera noise patterns / PRNU**  
- **GAN fingerprint & synthetic texture traits**  
- **Metadata validation (EXIF, compression traces)**  
- **Semantic realism signals**  
- **LLM-weighted final decision model**  

Designed for cases where ML detectors fail (highly compressed or edited images).

---

# 📁 Repository Structure

```
SatyaMark/
│── AI/
│   ├── text/                 # Text verification system
│   ├── img_ml/               # ML-based AI image detection
│   ├── img_forensic/         # Forensic detection engine
│   ├── dataset/              # ai/real -> train/test folders
│   ├── connect.py            # Connects all LLMs
│   ├── LLMs.json             # Model configuration file
│   ├── marks_of_truth.py     # Label enums used in text verification
│   ├── verify.py             # Local test runner for all modules
│   ├── requirements.txt
│   └── __init__.py
└── venv/ (optional)
```

---

# 📌 File Responsibilities

### ✔ verify.py — Local Testing Script
Runs **all verification modules locally** using sample inputs present in the repository.  
Users only need to **uncomment the section they want to test**, then run the script.

---

### ✔ connect.py — Central LLM Connector
- Loads all models defined in `LLMs.json`  
- Builds HuggingFaceEndpoint / ChatHuggingFace clients  
- Keeps all models in a shared cache  
- Provides `get_llm(name)` to retrieve any model instantly  

---

### ✔ LLMs.json — Model Configuration File
Defines every LLM using a simple schema:

```json
{
  "name": "model_name",
  "model_id": "huggingface_model_id",
  "task": "conversversational or text-generation",
  "max_new_tokens": 256,
  "temperature": 0.2
}
```

Example from your repo:

```json
{
  "name": "deepseek_r1_distill_llama_8b",
  "model_id": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
  "task": "conversational",
  "provider": "auto",
  "do_sample": false,
  "temperature": 0.2,
  "max_new_tokens": 512,
  "repetition_penalty": 1.05
}
```

---

### ✔ marks_of_truth.py — Verification Labels Enum
Defines all result types used across text verification:

- CORRECT  
- INCORRECT  
- SUBJECTIVE  
- INSUFFICIENT  
- AI_GENERATED  
- PENDING  

---

### ✔ dataset/
Contains the entire training/testing set for image ML verification:

```
train/
   ai/
   real/
test/
   ai/
   real/
```

---

# 🏗️ Architecture Overview

```
                ┌────────────────────┐
                │     LLMs.json      │
                └──────────┬─────────┘
                           │
                      connect.py
                           │
        ┌───────────┬───────────────┬─────────────┐
        │           │               │             │
   Text Verify   Image ML     Image Forensic    Dataset
     (text/)     (img_ml/)     (img_forensic/)  (ai/real)
        │           │               │
        └───────────┴───────────────┴───────────┐
                                                │
                                            verify.py
                                                │
                                             Output
```

---

# ⚙️ Setup & Usage

All commands must be run from the **root directory**:

```
PS E:\FullStack\SatyaMark>
```

---

## 1️⃣ Create Virtual Environment (only first time, if not created)

```
python -m venv venv
```

---

## 2️⃣ Activate Virtual Environment (if not already active)

```
.\AI\venv\Scripts\activate
```

---

## 3️⃣ Install Dependencies (only if not installed)

```
pip install -r AI/requirements.txt
```

---

## 4️⃣ Run the Example Script

```
python -m AI.text.verify
```

### 🔧 Note:
Inside `verify.py`, **comment/uncomment** the part you want to test:

```python
# print(verify_text(statement))
# print(verify_img_ml(path))
# print(verify_img_forensic(path))
```

---

# 🧩 Final Note
SatyaMark is built to be:
- Modular  
- Extensible  
- Easy to integrate into microservices  
- Simple to scale with new models or datasets  

You can add new LLMs, new detectors, new forensic modules, or replace entire pipelines without breaking the architecture.

