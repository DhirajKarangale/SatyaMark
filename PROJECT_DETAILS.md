# SatyaMark: Comprehensive Project Architecture & Technical Details

## 🌐 Quick Links
- **Official Website:** [https://satyamark.js.org/](https://satyamark.js.org/)
- **React SDK:** [https://www.npmjs.com/package/satyamark-react](https://www.npmjs.com/package/satyamark-react)
- **GitHub Repository:** [https://github.com/DhirajKarangale/SatyaMark](https://github.com/DhirajKarangale/SatyaMark)
- **Demo Social Media:** [https://satyamark-demo-socialmedia.vercel.app/](https://satyamark-demo-socialmedia.vercel.app/)

> **Disclaimer:** SatyaMark is an open-source project in active development. Verification results should be treated as trust signals rather than absolute truth. The platform is designed to assist human judgment, not replace it.

---

## 1. What is SatyaMark?
Every day, millions of posts, articles, images, and videos are shared across the internet. While access to information has never been easier, verifying its authenticity has become increasingly difficult. Traditional fact-checking systems are often fragmented, slow, and disconnected from the platforms where content is consumed. At the same time, advances in AI have made generating convincing text and images easier than ever.

That challenge led to the creation of **SatyaMark** — an open-source, multi-modal content verification platform designed to help users and platforms evaluate the credibility of digital content in real-time.

### Trust Signals Instead of Truth Labels
One of the most important design decisions behind SatyaMark is avoiding absolute truth claims. It doesn't simply label content as "True" or "False." Instead, it provides:
- **Confidence Scores:** A percentage indicating how confident the system is in its assessment.
- **Explainable Reasoning:** A human-readable breakdown of why the verdict was reached.
- **Verification Marks:** Visual trust indicators that can be attached directly to content (e.g., ✅ Verifiable, ❌ Unverifiable, ✔️ Correct, ❗ Incorrect, 🤖 AI-Generated, 👤 Human-Generated).
- **Evidence-Backed Analysis:** Verification supported by contextual information rather than isolated AI predictions.

---

## 2. The Core Problem & Target Audience

### The Problem: Verification is Not Cheap
A single verification request may involve:
- Extracting factual claims
- Searching for supporting evidence
- Evaluating context
- Querying language models
- Analyzing images
- Running forensic checks
- Generating explainable verdicts

Trying to perform all of this synchronously would quickly result in slow response times and a poor user experience. The challenge was simple:
> *How can verification be computationally expensive while still feeling fast to users?*

The answer was to separate verification workloads from user-facing interactions using asynchronous processing (Redis Streams) and real-time communication (WebSockets).

### Who is it For?
- **Platforms & Forums:** Social networks, messaging apps, CMS providers, and news aggregators looking to combat misinformation natively.
- **Users:** Platform moderators, researchers, journalists, and the general public who need transparent, evidence-backed verdicts.

---

## 3. High-Level Architecture & Folder Structure

The SatyaMark ecosystem is decoupled and distributed. Each component is independently scalable.

```text
1. [Frontend Clients] (DemoMedia, Satyamark Portal, satyamark-react SDK)
      |
      |-- WebSocket: Live Updates / REST API for details --> 
      v
2. [Orchestrator Backend] (Node.js)
      |
      |-- Create Job (xAdd) / Memory-Aware Load Balancing --> 
      v
3. [Redis Streams] (Message Queues: Upstash & Render)
      |
      |-- Consume Stream (xReadGroup) --> 
      v
4. [AI Intelligence Layer] (Text Worker / Image Worker in Python)
      |
      |-- HTTP Webhook Callback --> 
      v
5. [Database Layer] (PostgreSQL Cache & Deduplication)
```

### Verified Folder Structure
```text
SatyaMark/
├── AI/                     # AI Verification Workers (Python)
│   ├── image/              # Image pipeline (Sightengine, TruthScan, 18+ local forensics)
│   ├── text/               # LangGraph text pipeline (Summarize, Verifiability, FactCheck, WebVerify)
│   └── verify.py           # Unified entry point for testing pipelines
├── Backend/                # Orchestrator & API (Node.js, Express, ws)
│   └── src/
│       ├── hash/           # SHA-256 caching utilities
│       ├── model/          # PostgreSQL Database layer
│       ├── redis/          # Job Queue management (Janitor, Transfer, EventBus)
│       ├── starter/        # HTTP callbacks and WebSocket server
│       └── utils/          # Core utilities (RateLimiting, Memory-aware Router)
├── Frontend/               # Client Layer (React / Vite)
│   ├── DemoMedia/          # Sandbox social media app demonstrating SDK integration
│   ├── Satyamark/          # Main central web portal for manual checks and results
│   └── satyamark-react/    # The published React SDK (npm) managing DOM & WebSockets
```

---

## 4. In-Depth Technical Deep Dive: Technologies Used

- **Client Ecosystem (React, Vite, NPM):** The `satyamark-react` SDK is built entirely in React to easily latch onto React refs (`useRef`). Internally, it is organized into core layers (`connectionManager.ts`, `status_controller.ts`, `eventBus.ts`, `process.ts`) to manage complex UI state without polluting the host app.
- **Orchestration Server (Node.js, Express, `ws`):** Node.js acts as "airport traffic control." It doesn't decide if content is true or false; it just moves data efficiently. It excels at asynchronous I/O, managing thousands of persistent WebSocket connections concurrently without blocking.
- **Distributed Queues (Redis Streams):** We use Redis **Streams** (`xAdd`, `xReadGroup`, `xAutoClaim`) rather than Pub/Sub because Streams provide event persistence, consumer groups, reliable delivery, and decoupled horizontal scaling.
- **Relational Persistence (PostgreSQL):** We use Postgres (`pg`) to persist verified objects (`text_results`, `image_results`). It acts as a massive deduplication caching layer.
- **AI Pipelines (Python, LangGraph, LangChain):** Python is the industry standard for ML. We use **LangGraph** to model our text verification pipeline as a strict, observable state-machine (Directed Acyclic Graph).
- **Retrieval & LLMs:** Anthropic Claude and Hugging Face act as primary inference engines, supported by Google Search & Serper APIs for live web scraping via Trafilatura.

---

## 5. The End-to-End Lifecycle: A Deep Technical Dive

This section details every component, from the moment a user views content to the moment a verification mark is rendered.

### Step 1: DOM Extraction & Handshake (Client Layer -> Orchestrator)
- **Initialization:** The host application calls `init({ app_id, user_id })` to establish a persistent, multiplexed WebSocket connection to the Node.js backend.
- **Content Processing:** The developer wraps a post with the `process(element, dataId)` function.
- **DOM Traversal:** The SDK recursively traverses the DOM tree of the target element. It smartly filters out hidden text and scripts, extracting only visible claims and valid image URLs.
- **Injection:** A `<div data-satyamark-status-container>` placeholder is registered.
- **Payload Transmission:** The extracted payload is sent over the WebSocket connection (`type: "verification_request"`) along with the generated `clientId` and `sessionId`.

### Step 2: Caching, Deduplication, & Rate Limiting
Viral content causes repeated verification requests. To save expensive AI processing time, the backend aggressively deduplicates:
- The backend immediately computes a cryptographic **SHA-256 hash** of the text or image.
- It queries PostgreSQL (`text_results` or `image_results` tables).
- **Cache Hit:** The backend retrieves the previous verdict and triggers the internal `redisEventBus`, instantly broadcasting the cached result back over the WebSocket.
- **Cache Miss:** The backend applies **Rate Limiting** based on the user's allowance. It sends a "Pending ⏳" status over the WebSocket and prepares to enqueue the job.

### Step 3: Memory-Aware Routing & Queues
- The backend utilizes a `RedisQueueManager`. Before sending the job to Redis, it runs an `INFO memory` command on the primary Redis instance (Render).
- If the RAM saturation is below a safe threshold (e.g., 23MB), it uses `xAdd` to push the job to `stream:ai:text:jobs` or `stream:ai:image:jobs`.
- If the RAM exceeds the threshold, it dynamically spills over and routes the job to a secondary Redis cluster (Upstash).

### Step 4: Autonomous Intelligence Layer (Redis Streams -> Python AI)

Separate asynchronous Python worker threads continuously poll the Redis Streams using `xReadGroup`. 

#### 4.1 Text Verification Pipeline (LangGraph DAG)
1. **Summarization (`summary/`):** Strips social media noise (engagement stats, timestamps) and uses an LLM to generate an extractive, clean summary of the core claims.
2. **Verifiability Check (`verifyability.py`):** Classifies the claim as **VERIFYABLE** (objective facts) or **UNVERIFYABLE** (opinions, predictions). If unverifiable, the job terminates immediately.
3. **Fact Check (LLM Internal Weights) (`factcheck.py`):** The LLM compares the summary against its internal knowledge. If the claim requires highly specific, recent, or ambiguous data, the LLM deliberately returns an **Insufficient** status to trigger live scraping.
4. **Web Search Verification (`websearch/`):** 
   - Uses the **Google Serper API** to find trusted sources (automatically filtering out social media/video domains).
   - Downloads raw HTML concurrently using **Trafilatura**.
   - Runs a **Map-Reduce** algorithm: (Map) chunks the HTML and extracts relevant sentences; (Reduce) an LLM evaluates the condensed evidence against the claim.
   - Outputs a final verdict, confidence score, and citation URLs.

#### 4.2 Image Verification Pipeline (Forensic Cascade)
Because deepfake detection is computationally heavy and unreliable with a single method, the image pipeline uses a strict fallback architecture.
1. **Sightengine API:** Primary check for AI generation probabilities.
2. **TruthScan API:** Secondary check (uploads to DigitalOcean Spaces, asynchronously polls for deepfake detection).
3. **Local Heuristics Engine (`heuristics/`):** If external APIs fail, it falls back to 18+ local scientific forensic modules:
   - **Cryptography:** Metadata extraction (EXIF), C2PA manifests, hidden watermark detection.
   - **Optical Physics:** Sensor Pattern Noise (PRNU) to detect camera hardware signatures (AI images lack these), Chromatic Aberration analysis, perspective physics.
   - **Statistical & Frequency:** FFT/DCT patterns, Benford's Law compliance on pixel distributions.
   - **Forgery Detection:** Error Level Analysis (ELA) for splicing, compression artifact analysis, patch analysis.
   - **AI Fingerprinting:** Latent diffusion artifacts, GAN perturbation robustness testing.
   - **Decision Engine:** Aggregates scores across all 18 domains to output a final `ai_score` and `real_score`.

### Step 5: Result Delivery & UI Injection
- **HTTP Callback:** Once the Python worker computes a final verdict, it sends a REST POST payload to the Node.js backend (`/ai-callback/text` or `/ai-callback/image`).
- **Database Persistence:** Express stores the result in PostgreSQL. This generates a unique `dbId` that allows the user to share a standalone link to the `Satyamark Portal` for detailed inspection.
- **Event Bus Broadcast:** The Node.js server emits an internal event via `redisEventBus`.
- **WebSocket Push:** The `ws-server.js` listens to the event bus, maps the job back to the original active `clientId`, and pushes the final JSON payload.
- **Client-Side Injection:** The `satyamark-react` SDK intercepts the WebSocket message. The internal `status_controller.ts` automatically locates the corresponding `data-satyamark-status-container` and dynamically renders the `<SatyaMarkIcon />` React component. 
- **User Interaction:** The user sees the mark change from Pending ⏳ to a definitive state (e.g., ✅). Hovering shows the reasoning tooltip, and clicking routes them to the centralized Portal for the full cryptographic receipt.

---

## 6. Self-Healing & Extensibility

### Self-Healing Architecture
SatyaMark ensures expensive jobs are never lost in the ether:
- **Job Janitor (`jobJanitor.js`):** A daemon periodically checks for abandoned jobs (e.g., if a Python worker crashes mid-processing) using `xAutoClaim` (PEL - Pending Entries List). It implements a 3-strike retry system. Irrecoverable jobs are routed to a Dead Letter Queue.
- **Job Transfer (`jobTransfer.js`):** Actively monitors saturated Redis clusters and reassigns unprocessed jobs to idle clusters, preventing deadlocks and memory OOM errors.

### Extensibility
The architecture was designed to evolve. Adding a new capability (e.g., Audio Verification) only requires:
1. Creating a new Python worker.
2. Subscribing to a new Redis stream.
3. Adding a new `/ai-callback` endpoint in Node.js.

---

## 7. Lessons Learned & Business Strategy

### Lessons Learned
Building SatyaMark reinforced several engineering principles:
- **Decouple expensive workloads** from user-facing systems.
- **Cache aggressively** when AI inference is costly.
- **Use real-time communication** to improve perceived performance.
- **Confidence is often more useful than certainty.**
- Verification is not purely an AI problem—it is a **distributed systems problem** involving scalability, transparency, and trust.

### Go-To-Market (GTM) Strategy
- **Pilots:** Target niche publishers, fact-checking NGOs, and community forums for initial SDK integration.
- **Partnerships:** Partner with CMS platforms and modern social networks looking for native trust & safety tools.
- **Developer Adoption:** Foster a strong open-source community around the forensic heuristic modules and React SDK.

### Revenue Streams
- **Tiered API/SDK Subscriptions:** While open-source, managed infrastructure provides tiered rate-limits for high-volume enterprise platforms.
- **Trust & Safety Analytics:** Premium dashboards for moderation teams, offering insights on misinformation trends, active bot campaigns, and automated content flagging capabilities.

---

*The long-term goal remains simple: **Build trust infrastructure that is open, transparent, and accessible.***

> **Note:** SatyaMark is actively under development and components like image forensics are currently in an experimental phase.
