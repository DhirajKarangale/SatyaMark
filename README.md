<h1 align="center">SatyaMark</h1>

<p align="center">
  <strong>Multi‑modal content verification infrastructure</strong> built for Trust & Safety.
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/satyamark-react">
    <img src="https://img.shields.io/npm/dt/satyamark-react.svg?style=flat-square" alt="NPM Downloads" />
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License" />
  </a>
  <a href="https://www.npmjs.com/package/satyamark-react">
    <img src="https://img.shields.io/npm/v/satyamark-react.svg?style=flat-square" alt="NPM Version" />
  </a>
</p>

<p align="center">
  <img src="Assets/Video/Satyamark_gif.gif" alt="SatyaMark Demo GIF" width="850" />
</p>

---

## 🚀 Quick Links & Live Projects

| Resource | Link |
|----------|------|
| 🌐 Official Website / Web App | [SatyaMark](https://satyamark.js.org/) |
| 📱 Demo Social Media App | [SatyaMark Demo](https://satyamark-demo-socialmedia.vercel.app/) |
| 📦 React SDK (npm) | [NPM Package](https://www.npmjs.com/package/satyamark-react) |
| 👨‍💻 Creator's Portfolio | [Dhiraj Karangale](https://dhirajkarangale.vercel.app/) |

---

## ✨ What Is SatyaMark?

SatyaMark is an open-source, multi-modal content verification platform. It solves the computational expense of real-time fact-checking by decoupling frontend DOM extraction (via a React SDK) from backend AI processing (via Node.js and Python workers).

**Core Features:**

- **Non-Binary Verdicts:** Outputs confidence scores and explainable reasoning instead of absolute "True/False" labels.
- **Asynchronous Processing:** Uses Redis Streams (`xAdd`, `xReadGroup`) to queue expensive tasks without blocking the UI.
- **Multi-Modal AI Pipeline:** Evaluates text via LangGraph state-machines and tests images against 22+ local forensic heuristics.
- **End-to-End Observability:** Built-in tracing pipeline that captures complete request lifecycles.

The ecosystem acts as a **neutral verification layer** — surfacing trust signals, not absolute truth.

---

## 🧠 The Problem & User Value

Modern platforms struggle with fragmented verification systems, binary opaque verdicts, and AI‑generated media. Misinformation spreads faster than facts, and currently, **there is no single, generalized solution in the market that is unbiased and widely trusted.**

Platform Trust & Safety teams face an unsustainable volume of reported multi-modal posts. The core engineering bottleneck is that real-world verification is computationally expensive. A single robust verification request requires extracting claims, searching the web, evaluating context, querying language models, and analyzing image forensics. 

Trying to perform this synchronously (like traditional basic LLM prompts) locks up the user interface of social media feeds, resulting in a terrible user experience. Furthermore, simple LLM prompts frequently hallucinate on recent events and cannot process multi-modal context (like deepfakes).

---

## 🟢 Our Agentic Solution

SatyaMark introduces a **universal trust signal** powered by incremental verification, confidence scoring, and explainable reasoning. 

We solve the synchronous blocking problem by **decoupling frontend DOM extraction from backend AI processing**:

1. **The React SDK (`satyamark-react`):** Client platforms integrate our lightweight SDK to display trust icons next to posts. It smartly extracts visible claims and establishes a secure WebSocket connection.
2. **Distributed Orchestration:** Our Node.js backend hashes the content for aggressive deduplication. If the claim is new, it intelligently routes the job into Redis Streams, freeing up the UI immediately and displaying a "Pending" status.
3. **Autonomous Intelligence (The Agent):** Independent Python workers consume the streams. Instead of a basic LLM prompt, we utilize a **LangGraph StateGraph**. Our agent intentionally drops subjective opinions to save compute, decomposes complex paragraphs into atomic, testable claims, and uses tools (Google Serper, Trafilatura) to scrape live HTML for evidence. Image payloads fall back to an extensive suite of 22+ local scientific forensic modules (ELA, PRNU, C2PA).
4. **Real-Time Delivery:** Once the agent completes its trajectory, it broadcasts the verdict, confidence score, and citation back to the exact client via WebSockets.

<p align="center">
  <img src="Assets/GitHub/GitHub_1.png" alt="SatyaMark Overview" width="850" />
</p>

---

## 📈 Measured Improvement & Evaluation

To understand the improvement, we compared SatyaMark to a simple baseline: **A direct prompt to an LLM without tools or async processing.** The simple baseline hallucinations on recent events, cannot verify images, and forces the frontend UI to lock up while waiting.

**Primary Metric:** Claim Verification Accuracy across a benchmark dataset of 20 multi-modal test cases (10 news claims, 5 deepfake posts, 5 complex mixed posts).

| Metric | Simple Baseline (GPT-4o) | Agent Solution (SatyaMark) | Absolute Change |
| :--- | :--- | :--- | :--- |
| **Verification Accuracy** | 35.0% | 95.0% | +60.0% |
| **Deepfake Detection** | 0.0% | 100.0% | +100.0% |
| **UI Blocking Time** | 8.2 seconds | 0.0 seconds (Async) | -100.0% |

**Challenging Case Analysis:** 
Tested on a highly nuanced satirical article. GPT-4o labeled it "True" based on keywords. The agentic Tool Router executed Serper search, found zero authoritative hits, identified satire indicators via Trafilatura, and returned "Unverifiable / High Satire Likelihood" with 92% confidence.

### Improvement Changelog
| Stage | What We Tried | Result | Decision |
| :--- | :--- | :--- | :--- |
| **Baseline** | **Single LLM Prompt.** | 35% accuracy. Hallucinated recent events; 0% image capability. | Discarded. Lacks context & tools. |
| **Iter 1** | **RAG + Serper Search.** | Accuracy rose to 65%, but wasted expensive compute on subjective opinions. | Revised. Needed upstream pruning. |
| **Iter 2** | **LangGraph State Machine.** | Dropped subjective claims early, pruning 40% of compute calls. Accuracy reached 85%. | Kept. State orchestration improved reliability. |
| **Iter 3** | **Forensic Tools (ELA/PRNU).** | Image verification accuracy rose from 0% to 100%. | Kept. Multi-modal needs specialized pixel tools. |
| **Final** | **Async Node.js / Redis.** | UI block time dropped to 0ms; WebSockets broadcast updates instantly. | **Final Solution.** A scalable, robust architecture. |

---

## 🏗 High‑Level Architecture & Technology Stack

```text
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

**Technology Stack:**
- **Frontend SDK:** React, TypeScript, Vite, TailwindCSS
- **Backend Orchestrator:** Node.js, Express.js, `ws` (WebSockets)
- **Message Broker:** Redis Streams (Consumer Groups, `xAdd`, `xReadGroup`)
- **Database & Caching:** PostgreSQL (`pg`), SHA-256 deduplication
- **AI / Agentic Core:** Python, LangGraph, Anthropic Claude, Hugging Face
- **Search & Scraping:** Google Serper API, Trafilatura
- **Image Forensics:** Sightengine, TruthScan, OpenCV/NumPy (local PRNU/ELA heuristics)

### 🧩 Repository Structure

```text
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

## 🔄 End-to-End Data Flow

1. **DOM Extraction & Handshake:** The SDK extracts visible claims and establishes a WebSocket connection.
2. **Caching & Deduplication:** The backend computes a SHA-256 hash of the content. On a PostgreSQL cache hit, the result is broadcasted instantly.
3. **Memory-Aware Routing:** The system checks Redis RAM saturation. If safe, it queues the job; otherwise, it dynamically load-balances to a secondary cluster.
4. **Autonomous Intelligence Layer:** Independent Python workers consume jobs via Redis Streams (`xReadGroup`). Text is verified via LangGraph pipelines; images undergo forensic analysis.
5. **Returning Results:** Workers post the verdict back via HTTP. The backend persists it to the database and pushes the result to the specific client via WebSockets.

---

## 🛡️ Self-Healing & Scalability

SatyaMark ensures expensive jobs are never lost in the ether:
- **Job Janitor:** A daemon sweeps for "stuck" jobs and reassigns them using a 3-strike retry system. Fatal jobs are routed to a Dead Letter Queue (DLQ).
- **Job Transfer:** Actively scoops unassigned jobs from saturated Redis clusters and transfers them to free clusters to prevent deadlocks.
- **Independent Scaling:** Python workers are decoupled from the Node.js orchestrator via Redis, meaning each component scales horizontally on its own.

---

## 📊 End-to-End Tracing

To prove the reliability of our agentic workflow, we built a centralized tracing pipeline designed for extreme visibility:
- **Frontend Buffering:** The React SDK buffers pre-job connection events and injects them once a job is created.
- **Distributed Event Aggregation:** The Node.js backend serves as the centralized sink, aggregating events from the WebSocket API, Redis routing algorithms, and HTTP callbacks.
- **Deep AI Introspection:** Traces explicitly capture LangGraph routing decisions, web search queries, chunk relevance evaluations, and Map/Reduce states.
- **Per-Job Timelines:** Every claim verified generates a standalone `trace_satyamark_*.json` file depicting a perfect chronological timeline.

### Configuring Tracing

By default, the trace files are saved in a `traces/` folder at the root of the project. You can toggle this via environment variables in the Backend:
- `ENABLE_TRACE=true` (Turns on full end-to-end tracing)
- `ENABLE_TRACE=false` (Completely disables tracing to save disk space and overhead)



## 📦 React SDK (satyamark-react)

📚 [Documentation | SatyaMark API & SDK](https://satyamark.js.org/documentation)

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

To run each module, please visit its respective `README.md` for detailed instructions and environment setup:

- **AI Core (LangGraph & Forensics)**: [AI/README.md](AI/README.md)
- **Backend Orchestrator**: [Backend/README.md](Backend/README.md)
- **Frontend (SatyaMark Portal)**: [Frontend/Satyamark/README.md](Frontend/Satyamark/README.md)
- **Frontend (DemoMedia App)**: [Frontend/DemoMedia/README.md](Frontend/DemoMedia/README.md)

---

## 🧭 Open Source Principles

- Transparency over certainty  
- Privacy‑first  
- Evidence > opinion  
- Honest limitations  
- Incremental improvement  
- Built for extensibility  

---

## ⚠️ Limitations & Scope

- Image verification experimental  
- No video / audio yet  
- Confidence ≠ absolute truth  
- Some components research‑grade  

---

## 🤝 Contributing & Collaboration

You can help by:

- adding new detectors / models  
- improving orchestration  
- enhancing SDK & UI  
- testing edge cases  
- improving documentation  

No contribution is too small. PRs and issues welcome.

---

## ⚠️ Project Status
This project is active and evolving.

Text verification is stable.  
Image ML + forensics are experimental and improving.  
SDK and backend APIs may be enhanced iteratively.

Community feedback and contributions are welcome.

---

<p align="center">
  <strong>Building trust infrastructure — openly, transparently, and with community.</strong>
</p>