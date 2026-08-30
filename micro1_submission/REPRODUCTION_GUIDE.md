# SatyaMark: Reproduction Guide

This guide will walk you through setting up the entire SatyaMark infrastructure from a clean environment. SatyaMark is a distributed B2B SaaS system designed to provide a universal "mark of truth." You will run four distinct components: The Node.js Orchestrator, the Python Text Worker, the Python Image Worker, and the React Frontend (which integrates our `satyamark-react` SDK).

## Prerequisites
- Node.js (v18+)
- Python (3.9+)
- Redis (Running locally on default port `6379`, or accessible via a remote URI)
- PostgreSQL (Running locally, or a remote DB)

---

## 1. Environment Setup

### Database (PostgreSQL)
Connect to your PostgreSQL instance and create the required tables by running the SQL commands found in `Backend/README.md`.

### Environment Variables
1. Navigate to the `Backend` folder and create a `.env` file based on the instructions in `Backend/README.md` (fill in your DB and Redis URIs). Ensure you set `ENABLE_TRACE=true` to enable the end-to-end tracing system for the hackathon evaluation.
2. Navigate to the `AI` folder and create a `.env` file containing your `SERPER_API_KEY` (for web scraping) and any required model tokens as per `AI/README.md`.

---

## 2. Starting the Infrastructure

Open four separate terminal windows.

**Terminal 1: Node.js Orchestrator (Backend)**
```bash
cd Backend
npm install
npm start
```
*Expected Output:* You should see logs confirming connection to PostgreSQL, Redis, and the WebSocket server listening on port 1000.

**Terminal 2: Python AI Text Worker**
```bash
cd AI
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cd text
python ./starter/text_worker.py
```
*Expected Output:* The worker will announce it is polling the Redis stream `stream:ai:text:jobs`.

**Terminal 3: Python AI Image Worker (For Multi-Modal Forensics)**
```bash
cd AI
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
cd image
python ./starter/image_worker.py
```
*Expected Output:* The worker will announce it is polling the Redis stream `stream:ai:image:jobs`.

**Terminal 4: React Frontend (DemoMedia App)**
```bash
cd Frontend/DemoMedia
npm install
npm run dev
```
*Expected Output:* Vite will start the frontend. Open `http://localhost:5173` in your browser. This app demonstrates the client-side integration of the `satyamark-react` SDK.

---

## 3. Running the Evaluation

1. Open the DemoMedia app in your browser.
2. You will see a feed of posts. Notice the "Pending" verification marks.
3. **Observe the auto-verification:** Scroll down to a post containing a complex claim or an image. The SDK automatically detects it.
4. **Observe the UI:** The UI does not freeze. The WebSocket connection is established.
5. **Observe the Terminals:** 
   - Watch the Node.js backend receive the request via WS and dispatch it to Redis.
   - Watch the Python text or image workers pick up the job, run the LangGraph web-search nodes or image forensics, and post the result back.
   - Watch the React UI instantly update from "Pending" to the appropriate mark (e.g., Correct, Incorrect, Unverifiable, or AI-Generated).

---

## 4. Reviewing the Agent Trajectories (Traces)

Because you set `ENABLE_TRACE=true`, the system recorded the entire chronological lifecycle of that specific job.

1. Navigate to the root `traces/` folder in the repository.
2. Open the latest `trace_satyamark_<jobId>.json` file.
3. Inside, you will see the full agentic workflow: from the initial WebSocket handshake, through the Redis queue, into the exact LangGraph routing decisions (e.g., dropping subjective claims, scraping URLs, or running local image forensics), all the way to the final HTTP callback.
