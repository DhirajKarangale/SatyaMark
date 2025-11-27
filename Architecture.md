# SatyaMark — Complete System Architecture (Final Version)

This README describes the **final verified architecture** of SatyaMark based entirely on your requirements.
It is **clean, structured, accurate**, and uses **correct service names** that match your workflow.

---

# 🚀 1. High-Level Purpose

SatyaMark verifies text using multiple AI pipelines.
Because some AI jobs take **3–8 minutes**, the system is designed as **asynchronous, distributed, fault‑tolerant**, and **scalable** using:

* Multiple Node.js services
* Python AI inference workers
* Redis Streams for job queuing
* WebSockets for real-time result delivery
* PostgreSQL for permanent storage
* Independent Auth + Rate-Limit services

---

# 🧩 2. Final System Flow (Short Summary)

```
Frontend → API Gateway → Auth & Rate-Limit Services → Backend Service
     → AI Service (enqueue job) → Redis Streams → Worker(s)
     → Result Receiver → DB + Cache → WebSocket Service → Frontend
```

---

# 🔧 3. Services and Their Responsibilities

Below are the **final correct service names** and their exact responsibilities.

---

## 3.1 Frontend (React)

* Sends payload to **API Gateway** using JWT.
* Opens a WebSocket connection to receive final results.
* Maps results to the correct payload using `taskId`.

---

## 3.2 API Gateway (Node.js)

* Public-facing service receiving all requests from frontend.
* Extracts JWT from headers.
* Calls **Auth Service** to verify identity.
* Calls **Rate-Limit Service** to check whether user is allowed.
* Forwards valid requests to **Backend Service**.
* Only handles routing + lightweight logic.

---

## 3.3 Auth Service (Node.js)

* Issues JWT tokens.
* Validates tokens for API Gateway.
* Stores user credentials.
* Does not interact with AI / tasks.

---

## 3.4 Rate-Limit Service (Node.js)

* Centralized rate limiting.
* Uses Redis to store per-user request tokens.
* API Gateway queries: "Is this request allowed?"
* Ensures protection from spam or overuse.

---

## 3.5 Backend Service (Node.js)

This is the **core business service**.

Responsibilities:

* Reads JWT userId from the API Gateway.
* Computes:

  * `textHash`
  * `summaryHash`
* Checks Redis cache for previous results.
* If cache **HIT** → returns result immediately.
* If cache **MISS**:

  * Generates a `taskId`.
  * Stores initial task record in DB.
  * Calls **AI Service** to enqueue job.
* Returns `{ taskId, queued: true }` to frontend.

---

## 3.6 AI Service (Python FastAPI)

* Lightweight microservice.
* Does **NOT** run any AI models.
* Exposes:

  * `POST /enqueue` → inserts job into Redis Stream.
* Receives from Backend Service a job containing:

  * `taskId`
  * `userId`
  * `textHash`
  * `summaryHash`
  * `payload`
  * `callback_url`
  * `job_token` (for security)

---

## 3.7 Redis Streams (Upstash Redis)

Acts as the **distributed, reliable message queue**.

Why Redis Streams:

* Supports consumer groups (multiple workers)
* Guarantees one-worker-per-job
* Retries using XPENDING + XCLAIM
* Free tier available

Stream name example:

```
ai:jobs
```

---

## 3.8 Workers (Python; GPU or CPU)

These are completely independent containers/processes.
You can run **many** workers to scale.

Worker responsibilities:

* Connect to Redis Stream as a consumer.
* Claim job → run AI inference.
* Compute: `mark`, `reason`, `confidence`.
* POST final result to **Result Receiver** at `callback_url`.
* Sign callback using `job_token` or HMAC.

Workers can crash → job stays pending in Redis → another worker claims it.

---

## 3.9 Result Receiver (Node.js)

Receives final result from workers.

Responsibilities:

* Validate job authenticity.
* Write final result to PostgreSQL.
* Write result to Redis cache.
* Notify WebSocket Service that this user has new data.

This service is **write-only** and does NOT talk to frontend.

---

## 3.10 WebSocket Service (Node.js)

* Dedicated WebSocket server.
* Maintains mapping: `userId → list of socketIds`.
* Receives event from Result Receiver.
* Pushes final result JSON to correct user.
* Stateless → socket registry stored in Redis.

---

# 🗂️ 4. Data Flow (Step by Step)

### Step 1 — Frontend → API Gateway

```
POST /verify-text
Authorization: Bearer <JWT>
payload: {...}
```

### Step 2 — API Gateway

* Validates JWT via Auth Service.
* Checks rate limits via Rate-Limit Service.
* Forwards request to Backend Service.

### Step 3 — Backend Service

* Calculates `textHash` and `summaryHash`.
* Checks Redis Cache.
* If MISS → generates `taskId` and sends job to AI Service.

### Step 4 — AI Service

```
POST /enqueue
```

* Inserts job into Redis Stream: `XADD ai:jobs * ...`

### Step 5 — Workers

* Consume jobs (`XREADGROUP`).
* Run inference → produce `{ mark, reason, confidence }`.
* POST `/ai-callback` to Result Receiver.

### Step 6 — Result Receiver

* Stores result in DB (Postgres).
* Caches result in Redis.
* Sends event to WebSocket Service.

### Step 7 — WebSocket Service

* Looks up socket(s) for that user.
* Pushes final result to frontend.

### Step 8 — Frontend

* Receives WebSocket event containing:

```
{
  taskId,
  mark,
  reason,
  confidence,
  textHash,
  summaryHash
}
```

* Maps result to correct UI element.

---

# 🗄️ 5. Database Schema (PostgreSQL)

### Table: `ai_results`

| Column       | Type      | Description                                     |
| ------------ | --------- | ----------------------------------------------- |
| id           | UUID PK   | taskId                                          |
| user_id      | UUID      | From JWT                                        |
| text_hash    | TEXT      | Hash of original text                           |
| summary_hash | TEXT      | Hash of summary                                 |
| mark         | VARCHAR   | Subjective / Correct / Incorrect / Insufficient |
| reason       | TEXT      | LLM explanation                                 |
| confidence   | FLOAT     | 0–1                                             |
| created_at   | TIMESTAMP | Auto                                            |
| updated_at   | TIMESTAMP | Auto                                            |

---

# 💾 6. Redis Keys

```
cache:result:<textHash>      → final result
cache:task:<taskId>          → task metadata
ws:user:<userId>             → socket list
stream: ai:jobs              → Redis Stream for workers
```

---

# 🏗️ 7. Folder Structure (Recommended)

```
/satyamark
  /frontend
  /api-gateway
  /auth-service
  /rate-limit-service
  /backend-service
  /ai-service
  /workers
    /text-worker
    /image-worker
  /result-receiver
  /ws-service
  /docs
```

---

# ⚙️ 8. Free Hosting Strategy (For Development)

* Frontend → **Vercel**
* Node services → **Render** or **Railway**
* AI API (no GPU) → **Render** or **Deta Space**
* Workers → **Local machine**, **HuggingFace Spaces**, **Kaggle**, **Colab**
* DB → **Neon.tech**
* Redis Streams → **Upstash (free)**

---

# 🎯 9. Summary

This architecture:

* Fully matches your intended flow
* Uses correct names for each service
* Ensures AI slowdown doesn’t block backend
* Supports unlimited workers
* Ensures single delivery to the correct user
* Enables result caching + real-time push
* Allows future scaling without redesign

If you want, I can now generate:

* A sequence diagram
* A PNG architecture diagram
* Boilerplate code for each service
