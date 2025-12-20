<p align="center">
  <img src="./assets/CoverImage_1.png" alt="SatyaMark React" width="100%" />
</p>

# satyamark-react

**satyamark-react** is the official React client library for **SatyaMark** — a real-time, AI-powered content verification infrastructure that surfaces clear, evidence-backed trust signals directly inside your UI.

It extracts text and images from rendered DOM elements, submits them for verification, and renders standardized credibility icons that update live as results arrive.

SatyaMark is built as **trust infrastructure**, not a fact-checking oracle.

<p align="center">
  <a href="https://github.com/YOUR_GITHUB_USERNAME/satyamark-react">GitHub Repository</a>
  ·
  <a href="https://www.npmjs.com/package/satyamark-react">npm Package</a>
</p>

---

## What This Library Does

- Connects your React app to the SatyaMark verification network
- Extracts visible text and images from DOM elements
- Submits content for real-time verification
- Displays standardized trust icons inside your UI
- Updates verification status live
- Allows users to open detailed verification explanations

This library prioritizes **transparency over certainty**.

---

## Installation

```bash
npm install satyamark-react
```

---

## Quick Start

### 1. Initialize the SatyaMark connection (once)

```tsx
import { useEffect } from "react";
import { init, onConnected } from "satyamark-react";

useEffect(() => {
  init({
    app_id: "YOUR_APP_ID",
    user_id: "USER_ID",
  });
}, []);

onConnected((data) => {
  console.log("Connected to SatyaMark:", data);
});
```

---

### 2. Process content from a DOM element

`satyamark-react` works directly on **rendered UI**, not raw strings.

```tsx
import { useRef, useEffect, useState } from "react";
import { process, registerStatus } from "satyamark-react";

const cardRef = useRef<HTMLDivElement>(null);
const [jobId, setJobId] = useState<string | null>(null);

useEffect(() => {
  if (!cardRef.current) return;

  process(cardRef.current, "POST_ID")
    .then(setJobId)
    .catch(console.error);
}, []);
```

---

### 3. Display verification status

Add a container where the status icon should appear:

```tsx
<div satyamark-status-container />
```

Register the status handler:

```tsx
useEffect(() => {
  if (!jobId || !cardRef.current) return;

  registerStatus(jobId, cardRef.current);
}, [jobId]);
```

---

## How It Works

<p align="center">
  <img src="./assets/CoverImage_2.png" alt="SatyaMark Architecture" width="90%" />
</p>

1. Extracts visible text + first valid image  
2. Sends content via WebSocket  
3. Receives live verification updates  
4. Updates icons automatically  
5. Click icon → open detailed verification page  

---

## Verification Marks

- `correct`
- `incorrect`
- `verifyable`
- `unverifyable`
- `insufficient`
- `pending`
- `ai`
- `nonai`

---

## API Reference

### `init()`

```ts
init({
  app_id: string;
  user_id: string;
});
```

---

### `process()`

```ts
process(
  rootElement: HTMLDivElement,
  dataId: string
): Promise<string>
```

---

### `registerStatus()`

```ts
registerStatus(
  jobId: string,
  rootElement: HTMLElement,
  options?: {
    iconSize?: number;
  }
);
```

---

### `onReceive()`

```ts
onReceive((data) => {
  console.log(data);
});
```

---

### `onConnected()`

```ts
onConnected((connection) => {
  console.log("Connected:", connection);
});
```

---

## Design Principles

- Transparency over certainty  
- Trust signals, not guarantees  
- Privacy-first  
- Incremental accuracy  

---

## Current Limitations

- Text verification is most reliable  
- Image verification is experimental  
- Video & audio not yet supported  
- Results are not absolute truth  

---

## Privacy Notes

- Original text is not stored  
- Short AI-generated summaries may be retained  
- Images may be temporarily cached  
- No advertising or profiling  

---

## One-Line Summary

**satyamark-react lets React apps surface real-time, evidence-backed credibility signals directly inside the UI.**
