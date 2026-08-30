# Satyamark - AI-Powered Content Verification

## The Problem: The Internet Lacks a Unified Trust Signal
Misinformation and AI-generated media spread faster than facts across social platforms, causing confusion and mistrust. Currently, **there is no single, generalized solution in the market that is unbiased and widely trusted by the public.** Existing fact-checking systems are fragmented, incredibly slow, and completely disconnected from the platforms where content is actually consumed. 

The core engineering bottleneck is that real-world verification is computationally expensive. A single robust verification request requires extracting claims, searching the web, evaluating context, querying language models, and analyzing image forensics. Trying to perform this synchronously locks up the user interface of social media feeds, resulting in a terrible user experience. Because of this, platforms rely on basic, opaque LLM prompts that frequently hallucinate on recent events and cannot process multi-modal context.

## Our Agentic Solution
SatyaMark is a fast, secure, multi-modal content verification infrastructure designed to provide a universal "mark of truth." When users see the SatyaMark icon next to a post on any social media platform, they immediately experience a sense of trust: *"Oh, this is accurate."* It surfaces trust signals (confidence scores and explainable reasoning), rather than opaque absolute truth.

We solve the synchronous blocking problem by **decoupling frontend DOM extraction from backend AI processing**. 

1. **The React SDK (`satyamark-react`):** Client platforms integrate our lightweight SDK to display trust icons next to posts. It smartly extracts visible claims and establishes a secure, HMAC-validated WebSocket connection.
2. **Distributed Orchestration:** Our Node.js backend hashes the content for aggressive deduplication. If the claim is new, it intelligently routes the job into Redis Streams, freeing up the UI immediately and displaying a "Pending" status.
3. **Autonomous Intelligence (The Agent):** Independent Python workers consume the streams. Instead of a basic LLM prompt, we utilize a **LangGraph StateGraph**. Our agent intentionally drops subjective opinions to save compute, decomposes complex paragraphs into atomic, testable claims, and uses tools (Google Serper, Trafilatura) to scrape live HTML for evidence. Image payloads fall back to an extensive suite of 22+ local scientific forensic modules (ELA, PRNU, C2PA).
4. **Real-Time Delivery:** Once the agent completes its trajectory, it broadcasts the verdict, confidence score, and citation back to the exact client via WebSockets.

## Business Use Case & Go-To-Market
SatyaMark is not just a consumer app; it is **trust infrastructure** built for enterprise scale. 

**Target Audience:**
- Social networks and decentralized platforms (e.g., **Twitter/X, Bluesky, Mastodon, Reddit**), messaging apps, and news aggregators looking to combat misinformation natively without building internal AI infrastructure.
- Moderators, researchers, and journalists who need fast, secure, and evidence-backed verdicts.

**Go-To-Market Strategy:**
We are currently piloting the React SDK (which already has **3.1K+ npm downloads**) with niche publishers and fact-checking NGOs. By fostering developer adoption, we create a standardized, universal trust signal across the internet.

## Monetization Strategy
We monetize the massive compute required to run agentic fact-checking at scale:

1. **Tiered Enterprise API Subscriptions:** Platforms pay a tiered monthly SaaS fee based on API volume (monthly verification requests). Higher tiers include advanced features like custom LLM integration, faster Redis queues, and priority SLA.
2. **Trust & Safety Analytics Dashboard:** A premium, paid portal for enterprise moderation teams. It provides deep-dive analytics into misinformation trends on their platform, active bot-campaign identification, and automated flagging tools.
3. **Trace Validation & Auditing:** Charging for cryptographic verification receipts and compliance audits for regulated news organizations.

## Technical Details & Reproducibility
**Tech Stack:**
- **AI Core:** Python, LangGraph, LangChain, RAG, Claude/HF, Google Serper, 22+ Image Forensic Heuristics.
- **Backend Orchestrator:** Node.js, Express, WebSockets, PostgreSQL (Caching), Redis Streams (Message Queues).
- **Frontend Ecosystem:** React, Vite, TailwindCSS (`satyamark-react` NPM package).

**End-to-End Tracing:**
To prove the reliability of our agentic workflow, we built a centralized tracing pipeline. From the moment the React SDK initializes, to the Redis queue routing, down to the exact LangGraph chunk relevance evaluations, every decision the agent makes is passively instrumented and dumped into a chronological, per-job JSON trace file.

## Quick Links
- **Live Portal / App:** [https://satyamark.js.org/](https://satyamark.js.org/)
- **React SDK (npm):** [https://www.npmjs.com/package/satyamark-react](https://www.npmjs.com/package/satyamark-react)
- **Social Media Demo:** [https://satyamark-demo-socialmedia.vercel.app/](https://satyamark-demo-socialmedia.vercel.app/)
- **GitHub Repository:** [https://github.com/DhirajKarangale/SatyaMark](https://github.com/DhirajKarangale/SatyaMark)

*SatyaMark is actively redefining how the internet handles truth. It's built for scale, designed for transparency, and ready to be integrated today.*
