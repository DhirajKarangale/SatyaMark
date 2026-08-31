# SatyaMark Backend

SatyaMark Backend is the **central real-time verification engine** powering SatyaMark’s trust infrastructure.  
It receives verification requests from clients, intelligently routes them to AI workers, caches results, and streams verified outcomes back to clients in real time.

This backend **does not decide truth by itself** — it **coordinates verification**, stores results, and ensures fast, transparent delivery.

---

## What This Backend Does

At a high level, the backend acts as a **verification orchestrator**:

- Accepts **text or image verification requests**
- Checks **cached results** to avoid duplicate work
- Pushes new tasks into **Redis Streams**
- Receives AI worker callbacks
- Stores verified results in **PostgreSQL**
- Streams results to clients via **WebSockets**

---

## Basic Architecture

Client → WebSocket → SatyaMark Backend  
SatyaMark Backend → Redis Streams → AI Workers  
AI Workers → Callback → Backend → PostgreSQL → WebSocket → Client

---

## Tech Stack

- Node.js + Express
- WebSockets (`ws`)
- Redis (Streams)
- PostgreSQL
- SHA-256 hashing
- EventEmitter

---

## Supported Verification Types

- Text verification (stable)
- Image verification (experimental)

---

## Environment Setup

**Prerequisites:** Node.js (v18+), Local Redis (Port 6379), Local PostgreSQL.

Create a `.env` file from the example, and fill it with your real configuration (or use the command below):
```bash
# On Mac/Linux
cp .env.example .env

# On Windows (Command Prompt)
copy .env.example .env
```
Open the newly created `.env` file in your editor and input your real credentials for the following keys:
- **Database:** PostgreSQL connection string
- **Redis Orchestration:** `REDIS_RENDER_TEXT_URL`, `REDIS_UPSTASH_TEXT_URL`, `REDIS_RENDER_IMAGE_URL`, `REDIS_UPSTASH_IMAGE_URL`
- **Tracing:** Set `ENABLE_TRACE=true` to generate chronological trajectory logs.

---

## Database Tables

### text_results
```sql
CREATE TABLE text_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  text_hash TEXT,
  summary_hash TEXT,
  mark TEXT,
  reason TEXT,
  summary TEXT,
  confidence NUMERIC,
  urls TEXT[],
  received_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

### image_results
```sql
CREATE TABLE image_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  image_hash TEXT,
  image_url TEXT,
  mark TEXT,
  reason TEXT,
  confidence NUMERIC,
  received_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

---

## Run Locally (Full-Stack Evaluation)

Connect to your PostgreSQL instance and create the required tables (listed above) before starting the server.

```bash
npm install
npm start
```

Server runs on `http://localhost:1000`.

---

## WebSocket Usage

### Handshake
```json
{ "type": "handshake", "clientId": "client-1" }
```

### Verification Request
```json
{
  "clientId": "client-1",
  "jobId": "job-1",
  "text": "Claim to verify"
}
```

---

## Design Principles

- Transparency over certainty
- Cache before compute
- Async by default
- Privacy-first

---

## Summary

**SatyaMark Backend is a scalable, real-time verification orchestrator connecting users, AI workers, and trust signals.**
