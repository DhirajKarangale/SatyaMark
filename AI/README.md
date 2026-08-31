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
- Python (3.9+)
- Redis (for production workers)

### 2. Configure Environment Variables
Copy the `.env.example` file and rename it to `.env` (or use the command below):
```bash
# On Mac/Linux
cp .env.example .env

# On Windows (Command Prompt)
copy .env.example .env
```
Open the newly created `.env` file in your editor and input your real credentials for the following keys:
- **LLM & Search APIs:** `ANTHROPIC_API_KEY`, `HF_TOKENS`, `SERPER_API_KEYS`
- **Forensic APIs:** `TRUTHSCAN_API_KEY`, `SIGHTENGINE_API_USERS`, `SIGHTENGINE_API_SECRET`
*(Resource Note: Agent testing costs roughly $0.14 per 20 runs. Image forensics are heavily API-dependent).*

### 3. Installation
Clone the repository and set up a virtual environment:
```bash
git clone https://github.com/DhirajKarangale/SatyaMark.git
cd SatyaMark/AI

python -m venv venv

# Activate the virtual environment:
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

---

## ▶️ Usage

### Fast AI Evaluation (Local Testing)
Use the unified entry point to run localized tests directly on the LangGraph state machine and Forensic heuristics.

1. **Select a Test Case:** Open `verify.py`. On lines 39-40, modify the `ACTIVE_TEXT` or `ACTIVE_IMAGE` variables to input the claim or image URL you wish to verify.
2. **Execute the Agent:**
```bash
python verify.py
```
**Expected Output:** The console will trace the agent's trajectory and output a final structured verdict with confidence scores and citations.

### Production Workers (Full-Stack Evaluation)
For production deployments or the Full-Stack Evaluation method, the system consumes jobs asynchronously via Redis.

**Start the Text Worker:**
```bash
cd text
python ./starter/text_worker.py
```

**Start the Image Worker:**
```bash
cd image
python ./starter/image_worker.py
```

---

## ⚠️ Disclaimer
This system provides **trust signals and probabilistic evaluations**, not absolute truth. Always use critical thinking in conjunction with the system's confidence scores and explanations.
