<h1 align="center">SatyaMark</h1>

<p align="center">
  Open‑source <strong>multi‑modal content verification infrastructure</strong> with an official React SDK for platform integration.
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/satyamark-react">
    <img src="https://img.shields.io/npm/v/satyamark-react.svg" />
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" />
  </a>
</p>

---

## ⚠️ Project Status

> **This project is active and evolving.**

Text verification is stable.  
Image ML + forensics are experimental and improving.  
SDK and backend APIs may be enhanced iteratively.

Community feedback and contributions are welcome.

---

## ✨ What Is SatyaMark?

SatyaMark is an open‑source project that includes:

- 🧠 **AI verification workers** — Text fact‑checking, AI‑image detection, forensics  
- ⚙️ **Backend orchestrator** — Redis Streams + WebSockets + PostgreSQL  
- 🎨 **Frontend web app** — Result viewer & manual verification  
- 📦 **Published React SDK** — `satyamark-react` for platform embedding

It acts as a **neutral verification layer** — surfacing trust signals, not absolute truth.

---

## 🚀 Live Projects & SDK

| Component | Link |
|----------|------|
| 🖥️ Main Verification App | https://satyamark.vercel.app/ |
| 📱 Demo Social Media App | https://satyamark-demo-socialmedia.vercel.app/ |
| 📦 React SDK (npm) | https://www.npmjs.com/package/satyamark-react |

---

## 🧠 The Problem

Modern platforms struggle with:

- fragmented verification systems  
- binary & opaque verdicts  
- AI‑generated and manipulated media  
- lack of transparency  
- no universal trust mark  

There is **no shared, real‑time verification infrastructure for the internet.**

---

## 🟢 The SatyaMark Solution

SatyaMark introduces a **universal trust signal** powered by:

- incremental verification
- confidence scoring
- explainable reasoning
- cross‑platform consistent marks
- integration via SDK

It is **trust infrastructure**, not a fact‑checking authority.

---

## 🏗 High‑Level Architecture

```
Client Platforms (via satyamark-react)
        │
        ▼
Backend (Orchestration + Storage + Streams)
        │
        ▼
AI Workers (Text / ML / Forensics)
        │
        ▼
Verdicts + Confidence + Explanation
```

<p align="center">
  <img src="Assets/GitHub/GitHub_3.png" alt="SatyaMark Architecture Overview" width="850" />
</p>

---

## 🧩 Repository Structure

```
SatyaMark/
├── AI/                     # Verification workers
├── Backend/                # Redis + WS + DB orchestrator
├── Frontend/
│   ├── Satyamark/          # Main web app
│   ├── DemoMedia/          # Social media demo
│   └── satyamark-react/    # React SDK (npm)
├── Assets/
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
└── README.md
```

👉 This is a framework — not a single application.

---

## 📦 React SDK (satyamark-react)

Install:

```bash
npm install satyamark-react
```

Minimal usage:

```tsx
process(ref.current, post.id);
registerStatus(jobId, ref.current);
```

The SDK enables any React platform to embed SatyaMark trust marks in real time.

---

## 🧪 Run Locally

```bash
git clone https://github.com/DhirajKarangale/SatyaMark.git
cd SatyaMark
```

Run components:

- AI → `cd AI && python verify.py`
- Backend → `cd Backend && npm install && npm start`
- Frontend → `cd Frontend/Satyamark && npm install && npm run dev`

See sub‑README for environment variables.

---

## 🧭 Open Source Principles

- Transparency over certainty  
- Privacy‑first  
- Evidence > opinion  
- Honest limitations  
- Incremental improvement  
- Built for extensibility  

---

## Limitations & Scope

- Image verification experimental  
- No video / audio yet  
- Confidence ≠ absolute truth  
- Some components research‑grade  

---

<p align="center">
  <img src="Assets/GitHub/GitHub_1.png" alt="SatyaMark Overview" width="850" />
</p>

---

## 🤝 Contributing & Collaboration

You can help by:

- adding new detectors / models  
- improving orchestration  
- enhancing SDK & UI  
- testing edge cases  
- improving documentation  

No contribution is too small.

PRs and issues welcome.

---

<p align="center">
  <strong>Building trust infrastructure — openly, transparently, and with community.</strong>
</p>
