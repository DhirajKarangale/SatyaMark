# SatyaMark — Multi-Modal Verification System

SatyaMark is an extensible AI framework for **Text Fact Verification** and **Image Forensic Verification**.
It provides modular pipelines, unified LLM connectors, and a scalable architecture for reliable verification.

---

# 📚 Verification Modules

## 📝 Text Verification System (LLM-Driven)

https://github.com/DhirajKarangale/SatyaMark/blob/main/AI/text/README.md

Evaluates statements as:
- CORRECT
- INCORRECT
- SUBJECTIVE
- INSUFFICIENT

Pipeline:
1. Subjectivity check  
2. Claim extraction  
3. Initial scoring  
4. Web search (fallback)  
5. Final verdict + explanation  

---

## 🔍 Image Verification

https://github.com/DhirajKarangale/SatyaMark/blob/main/AI/image/README.md

Core techniques:
- Sensor Pattern Noise (SPN)
- Metadata / EXIF validation
- Frequency & pixel analysis
- ELA & compression artifacts
- GAN / diffusion fingerprints
- Physics & geometry consistency

Produces:
- AI / NONAI / UNCERTAIN
- Confidence score
- Human-readable reasoning

---

# 🏗️ Architecture

```
            LLMs.json
                │
            connect.py
                │
        ┌───────────────┬───────────────┐
        │               │
   Text Verify     Image Verify
     (text/)        (image/)
        │               │
        └───────────────┘
                │
            verify.py
                │
             Output
```

---

# ⚙️ Setup

## Clone
```
git clone https://github.com/DhirajKarangale/SatyaMark.git
cd SatyaMark/AI
```

## Virtual Env
```
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

## Install
```
pip install -r requirements.txt
```

## .env
```
SERPER_API_KEY=your_key
HF_TOKEN=your_token
REDIS_URL=your_url
```

---

# ▶️ Usage

## Local Test
```
python verify.py
```

---

## Workers (Production)

### Text Worker
```
cd AI/text
python ./starter/text_worker.py
```

### Image Worker
```
cd AI/image
python ./image_worker.py
```

---

# Disclaimer

Not 100% accurate. Use critical thinking.
