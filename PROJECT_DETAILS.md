# SatyaMark: Open-Source Multi-Modal Content Verification Infrastructure

## 🌐 Quick Links
- **Official Website:** [https://satyamark.js.org/](https://satyamark.js.org/)
- **React SDK:** [https://www.npmjs.com/package/satyamark-react](https://www.npmjs.com/package/satyamark-react)
- **GitHub Repository:** [https://github.com/DhirajKarangale/SatyaMark](https://github.com/DhirajKarangale/SatyaMark)
- **Demo Social Media:** [https://satyamark-demo-socialmedia.vercel.app/](https://satyamark-demo-socialmedia.vercel.app/)
- **Portfolio:** [https://dhirajkarangale.vercel.app/](https://dhirajkarangale.vercel.app/)

> **Disclaimer:** SatyaMark is an open-source project in active development. Verification results should be treated as trust signals rather than absolute truth. The platform is designed to assist human judgment, not replace it.

---

## 1. What is SatyaMark?

Every day, millions of posts, articles, images, and videos are shared across the internet. While access to information has never been easier, verifying its authenticity has become increasingly difficult. Traditional fact-checking systems are often fragmented, slow, and disconnected from the platforms where content is consumed. At the same time, advances in AI have made generating convincing text and images easier than ever.

That challenge led to the creation of **SatyaMark** — an open-source, multi-modal content verification platform designed to help users and platforms evaluate the credibility of digital content in real-time.

### Trust Signals Instead of Truth Labels
One of the most important design decisions behind SatyaMark is avoiding absolute truth claims. It doesn't simply label content as "True" or "False." Instead, it provides:
- **Confidence Scores:** A percentage indicating how confident the system is in its assessment.
- **Explainable Reasoning:** A human-readable breakdown of why the verdict was reached.
- **Verification Marks:** Visual trust indicators that can be attached directly to content.
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

The answer was to separate verification workloads from user-facing interactions using asynchronous processing and real-time communication.

### Who is it For?
- **Platforms & Forums:** Social networks (Facebook, Twitter, Reddit), online forums, messaging apps, CMS providers, and news aggregators looking to combat misinformation natively.
- **Users:** Platform moderators, researchers, journalists, and the general public who need transparent, evidence-backed verdicts.

---

## 3. High-Level Architecture & Folder Structure

The system is intentionally simple and decoupled. Each component has a specific responsibility and can scale independently when needed.

```text
1. [Client Layer] (React App / SDK)
      |
      |-- WebSocket: Live Updates --> 
      v
2. [Orchestration Layer] (Node.js Backend)
      |
      |-- Create Job (xAdd) --> 
      v
3. [Redis Streams] (Message Queues)
      |
      |-- Consume Stream (xReadGroup) --> 
      v
4. [Intelligence Layer] (Text Worker / Image Worker in Python)
      |
      |-- HTTP Callback --> 
      v
5. [Database Layer] (PostgreSQL Cache & DB)
```

### Verified Folder Structure
```text
SatyaMark/
├── AI/                     # AI Verification Workers (Python)
│   ├── dataset/            # Test datasets
│   ├── image/              # Image forensics pipeline (downloader, heuristics, sightengine, truthscan)
│   ├── text/               # LangGraph-based text verification pipeline (summary, verifyability, factcheck, websearch)
│   ├── .env                # API keys for LLMs and Google Search
│   ├── README.md           # Documentation for AI workers
│   ├── requirements.txt    # Python dependencies
│   └── verify.py           # Entry point to test the AI pipelines
├── Backend/                # Orchestrator & API (Node.js)
│   ├── .env                # Server configuration and API keys
│   ├── README.md           # Documentation for Backend
│   ├── package.json        # Node.js dependencies
│   └── src/
│       ├── hash/           # SHA-256 caching utilities (image_hash.js, text_hash.js)
│       ├── model/          # PostgreSQL Database layer (db.js, modelImage.js, modelText.js)
│       ├── redis/          # Job Queue management (jobJanitor.js, jobTransfer.js, manageRedis.js, redisClient.js)
│       ├── starter/        # HTTP callbacks and WebSocket server (callback.js, redisEventBus.js, ws-server.js)
│       └── utils/          # Core utilities (connectionManager.js, enqueueJob.js, process_task.js, rateLimiter.js)
├── Frontend/               # Client Layer (React / Vite)
│   ├── DemoMedia/          # Sandbox social media app demonstrating SDK integration
│   ├── Satyamark/          # Main central web portal for manual checks and results
│   └── satyamark-react/    # The published React SDK (npm) containing (connectionManager.ts, status_controller.ts)
```

---

## 4. In-Depth Technical Deep Dive: Technologies Used

- **Client Ecosystem (React, Vite, NPM):** The `satyamark-react` SDK is built entirely in React to easily latch onto React refs (`useRef`). Internally, it is organized into core layers (`connectionManager.ts`, `status_controller.ts`, `eventBus.ts`, `process.ts`) to manage complex UI state without polluting the host app.
- **Orchestration Server (Node.js, Express, `ws`):** Node.js acts as "airport traffic control." It doesn't decide if content is true or false; it just moves data efficiently. It excels at asynchronous I/O, managing thousands of persistent WebSocket connections concurrently without blocking.
- **Distributed Queues (Redis Streams):** We use Redis **Streams** (`xAdd`, `xReadGroup`, `xAutoClaim`) rather than Pub/Sub because Streams provide event persistence, consumer groups, reliable delivery, and decoupled horizontal scaling.
- **Relational Persistence (PostgreSQL):** We use Postgres (`pg`) to persist verified objects (`text_results`, `image_results`). It acts as a massive deduplication caching layer.
- **AI Pipelines (Python, LangGraph, LangChain):** Python is the industry standard for ML. We use **LangGraph** to model our text verification pipeline as a strict, observable state-machine (Directed Acyclic Graph).
- **Vector Retrieval & LLMs:** **FAISS / Milvus** is used in the RAG pipeline for semantic cosine-similarity searches. Anthropic Claude and Hugging Face act as primary inference engines, supported by Google Search & Serper APIs for live web scraping.

---

## 5. End-to-End Data Flow: The Lifecycle of a Verification Request

Here is the exact step-by-step lifecycle of how data moves from the library, to the AI, and back to the client.

### Step 1: DOM Extraction & Handshake (Client Layer -> Orchestrator)
- A developer integrates the SDK and wraps a post with `process(element, postId)`.
- The SDK recursively traverses the DOM tree, ignoring hidden text/scripts, and extracts only visible claims and valid image URLs.
- The SDK establishes a WebSocket connection with the Backend (`type: "handshake"`). Node.js assigns a unique `clientId` and `sessionId`.
- The payload is streamed over the WebSocket to the Backend's `process_task.js` router.

### Step 2: Caching, Deduplication, & Rate Limiting
A surprising amount of content gets verified repeatedly (viral posts, popular images). Without caching, the same content triggers expensive AI workflows over and over.
- The backend computes a cryptographic SHA-256 hash of the submitted content via `text_hash.js` or `image_hash.js`.
- It queries the PostgreSQL database via `modelText.GetText()` or `modelImage.GetImage()`.
- **Cache Hit:** If a match is found, the backend bypasses the AI completely and uses `redisEventBus` to instantly broadcast the result back over the WebSocket.
- **Cache Miss:** The backend checks user allowance via `rateLimiter.js`. If allowed, it prepares a job for the AI Workers and immediately returns a "Pending" status to the user.

### Step 3: Memory-Aware Routing (Orchestrator -> Redis Streams)
- The backend utilizes a `RedisQueueManager` (`enqueueJob.js`).
- Before enqueueing the job, it runs the Redis `INFO memory` command on the primary "Render" Redis instance to check RAM saturation.
- If RAM is under the safe threshold (e.g., 23MB), it executes `xAdd` to append the payload into `stream:ai:text:jobs`.
- If RAM exceeds the threshold, the router dynamically load-balances, spilling the job over to a secondary "Upstash" Redis instance.

### Step 4: Autonomous Intelligence Layer (Redis Streams -> Python AI)
Independent Python workers continuously consume jobs from Redis Streams using `xReadGroup`. Because they operate independently, they scale separately from the backend (if image verification is slow, we just spin up more image workers).

#### Text Worker Pipeline (LangGraph DAG)
1. **Subjectivity Detection (`verifyability.py`):** The system first determines if a statement contains objective claims. If subjective, it halts.
2. **Evidence Retrieval (`factcheck.py`):** The system searches trusted sources and internal knowledge bases using FAISS/Milvus.
3. **Web Scraper (`web_verify.py`):** If internal data is insufficient, it triggers live web scraping via Google APIs.
4. **Final Verdict:** Generates a confidence score, human-readable reasoning, and a categorical mark.

#### Image Worker Pipeline (22+ Heuristics)
To identify AI-generated or manipulated content, a structured fallback mechanism is used in `image_verify.py`:
1. **API Layers:** Passes through Sightengine and Truthscan deepfake detection.
2. **Deep Local Forensics (`heuristics/`):** The repository executes an extensive suite of 22 specialized local forensic scripts, including:
   - `diffusion_latent_analysis.py` (Detects stable diffusion artifacts)
   - `ela_analysis.py` (Error Level Analysis)
   - `c2pa.py` (Content Provenance tracking)
   - `sensor_pattern_noise.py` (PRNU Analysis)
   - `benfords_law.py`, `frequency_domain_analysis.py`, and `gan.py` for pixel-level synthesis detection.

### Step 5: Returning Results (Python AI -> PostgreSQL -> WebSocket -> UI)
- **HTTP Callback:** The Python worker synthesizes the final verdict and sends it via an HTTP POST request back to the Node.js orchestrator (`/ai-callback/text` or `image`).
- **Persistence:** Express saves the result to PostgreSQL, generating a `dbId` (which powers the standalone detail page URL).
- **Event Bus Broadcast:** The Express app triggers the internal `redisEventBus`. The WebSocket server (`ws-server.js`) listens for this, finds the active socket mapped to the `clientId`, and pushes the finalized payload.
- **UI Injection:** The React SDK intercepts the WebSocket message via `socketClient.ts` and routes it to `status_controller.ts`, which automatically injects the visual `<SatyaMarkIcon />` component into the DOM. No manual status polling is required from the host developer.

---

## 6. Self-Healing & Extensibility

### Self-Healing Architecture
SatyaMark ensures expensive jobs are never lost in the ether:
- **Job Janitor (`jobJanitor.js`):** A daemon runs periodically to sweep for "stuck" jobs (jobs claimed by a crashed worker, idle > 10 minutes) using `xAutoClaim`. It implements a 3-strike retry system. Fatal jobs are routed to a Dead Letter Queue (DLQ).
- **Job Transfer (`jobTransfer.js`):** Actively scoops unassigned jobs from saturated Redis clusters and transfers them to free clusters to prevent deadlocks.

### Extensibility
The architecture was designed to evolve. Adding a new verification capability (e.g., Audio or Video) generally requires:
1. Creating a new Python worker.
2. Consuming specific Redis events.
3. Adding a new `/ai-callback` endpoint on the backend.
Because responsibilities are clearly separated, new capabilities can be introduced without rewriting the rest of the system.

---

## 7. Lessons Learned & Business Strategy

### Lessons Learned
Building SatyaMark reinforced several engineering principles:
- Decouple expensive workloads from user-facing systems.
- Cache aggressively when AI inference is costly.
- Use real-time communication to improve perceived performance.
- Design for extensibility early.
- **Confidence is often more useful than certainty.**
- Verification is not purely an AI problem—it is a distributed systems problem involving scalability, transparency, and trust.

### Go-To-Market (GTM) Strategy
- **Pilots:** Pilot the SDK with niche publishers, fact-checking NGOs, and community forums.
- **Partnerships:** Partner with messaging apps and CMS platforms to embed the SDK natively.
- **Developer Adoption:** Foster adoption through comprehensive developer docs, sample integrations, and tech conferences.

### Revenue Streams
- **Tiered API / SDK Subscriptions:** Paid plans for platforms offering higher verification rate limits, advanced AI forensic features, and priority support.
- **Analytics Dashboard:** A premium dashboard offering trends, verified content stats, and real-time moderation alerts for platform trust & safety teams.

---

*The long-term goal remains simple: **Build trust infrastructure that is open, transparent, and accessible.***

> **Note:** SatyaMark is actively under development and components like image forensics are currently in an experimental phase.
