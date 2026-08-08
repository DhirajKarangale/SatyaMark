<h1 align="center">SatyaMark AI Core</h1>

<p align="center">
  The intelligence layer for the SatyaMark verification infrastructure, handling both <strong>Text Fact Verification</strong> and <strong>Image Forensic Verification</strong>.
</p>

---

## 🏗️ Architecture & Modules

The `AI` module is structured into two distinct domains, unified by a single local entry point (`verify.py`). In production, it relies on asynchronous queue workers to process verification tasks at scale.

```text
                     SatyaMark AI Core
                            │
                      verify.py (Unified Entry)
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
     Text Verification                Image Verification
  (AI/text/starter/text_verify.py)    (AI/image/image_verify.py)
            │                               │
    LangGraph Pipeline                 Fallback Pipeline
  1. summarize()                     1. sightengine API
  2. verifyability()                 2. truthscan API
  3. fact_check()                    3. 22+ local heuristics
  4. web_verify()                       (ELA, SPN, Metadata, etc.)
```

### 📝 Text Verification (`AI/text/`)
**[👉 View Detailed Text Verification Documentation](./text/README.md)**

A state-machine workflow built with LangGraph that processes claims, extracts key facts, attempts zero-shot LLM verification, and falls back to live web scraping to deliver a final verdict (`CORRECT`, `INCORRECT`, `SUBJECTIVE`, `INSUFFICIENT`). 

### 🔍 Image Verification (`AI/image/`)
**[👉 View Detailed Image Verification Documentation](./image/README.md)**

A robust cascading pipeline that attempts external model validation before falling back to a comprehensive suite of 22+ local forensic heuristics (e.g., Error Level Analysis, Sensor Pattern Noise, Metadata Validation, GAN/Diffusion Artifact Detection) to classify an image's origin and integrity.

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.9+
- Redis (for production workers)

### 2. Installation
Clone the repository and set up a virtual environment:
```bash
git clone https://github.com/DhirajKarangale/SatyaMark.git
cd SatyaMark/AI

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies (includes both text and image requirements)
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the `AI` directory with the following keys. (Make sure you also check the individual text and image documentation for any specific models you might be enabling/disabling):

```env
# Required for Text Web Search fallback
SERPER_API_KEY=your_serper_api_key

# Required for LLM integration (if using HF models)
HF_TOKEN=your_huggingface_token

# Required for Production Workers
REDIS_URL=redis://localhost:6379/0

# Optional API keys depending on active image verification services
SIGHTENGINE_API_USER=your_user
SIGHTENGINE_API_SECRET=your_secret
```

---

## ▶️ Usage

### Local Testing & Development
Use the unified entry point to run localized tests on both pipelines. You can modify the `statements` or `image_source` variables directly in `verify.py`.

```bash
python verify.py
```

### Production Workers
For production deployments, the system is designed to consume verification jobs asynchronously via Redis. Run these in separate terminal instances or as background services.

**Start the Text Worker:**
```bash
cd AI/text
python ./starter/text_worker.py
```

**Start the Image Worker:**
```bash
cd AI/image
python ./image_worker.py
```

---

## ⚠️ Disclaimer
This system provides **trust signals and probabilistic evaluations**, not absolute truth. Always use critical thinking in conjunction with the system's confidence scores and explanations.
