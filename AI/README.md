# SatyaMark — Multi-Modal Verification System

SatyaMark is an extensible AI framework designed for **Text Fact Verification**, **AI Image Detection (ML-based)**, and **Image Forensics Verification**.  
It brings together multiple detection pipelines, unified LLM connectors, and modular architecture for scalable, accurate verification across modalities.

---

# 📚 Verification Modules

Below are the three major verification systems included in SatyaMark, each with its own documentation.

---

## [📝 **Text Verification System (LLM-Driven Fact Checking)**](https://github.com/DhirajKarangale/SatyaMark/blob/main/AI/text/README.md)

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

## [🖼️ **Image Verification Using HuggingFace Models (ML-Based Ensemble)**](https://github.com/DhirajKarangale/SatyaMark/blob/main/AI/img_ml/README.md)

This module detects whether an image is **AI-generated or real** using:
- CLIP/Transformers semantic similarity  
- Embedding-based signals  
- Forensic-light cues  
- Metadata features  
- A trained **fusion classifier** (Logistic / LightGBM / etc.)  

---

## [🔍 **Image Verification Using Forensic Signals (Advanced Forensics)**](https://github.com/DhirajKarangale/SatyaMark/blob/main/AI/img_forensic/README.md)

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

## 1️⃣ Clone the Repository
```
git clone https://github.com/DhirajKarangale/SatyaMark.git
cd SatyaMark
```

## 2️⃣ Navigate to AI Engine
```
cd AI
```

## 3️⃣ Create Virtual Environment (first time only)

### Windows
```
python -m venv venv
```

### macOS/Linux
```
python3 -m venv venv
```

## 4️⃣ Activate Environment

### Windows
```
venv\Scripts\activate
```

### macOS/Linux
```
source venv/bin/activate
```

## 5️⃣ Install Dependencies
```
pip install -r requirements.txt
```

## 6️⃣ Create `.env`
```
SERPER_API_KEY=your_serper_key
HF_TOKEN=your_hf_token
REDIS_URL=your_upstash_redis_streams_url
```

## 7️⃣ Run Local Tests
```
python verify.py
```

Uncomment the test you want to run inside the file.

---

# 🧩 Final Note
SatyaMark is built to be:
- Modular  
- Extensible  
- Easy to integrate into microservices  
- Simple to scale with new models or datasets  

You can add new LLMs, new detectors, new forensic modules, or replace entire pipelines without breaking the architecture.

---

### **Note**
*Not 100% accurate. Honestly, nothing I build ever is. Good thing you have a real brain to verify stuff.*

---