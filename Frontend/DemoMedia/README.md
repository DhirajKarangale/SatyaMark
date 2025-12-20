# SatyaMark Demo – Social Media Use Case

A demo social media application showcasing how **SatyaMark** can be integrated into real-world platforms using the **`satyamark-react`** library to verify text and image content in real time.

This project demonstrates how credibility signals (trust marks, confidence, explanations) can be embedded directly into user-generated content feeds.

---

## 🌐 Live Demo

👉 **Live URL:** https://your-live-demo-url.com

> This live deployment demonstrates how SatyaMark verification works in a real social media–style feed.

---

## 🧪 About This Demo Project

This project is a **demo application** created to showcase the **use case of the `satyamark-react` library** in a social media–style environment.

It simulates how platforms can integrate SatyaMark to:
- Automatically verify user-generated content
- Display real-time verification marks
- Surface confidence and explanations directly in the UI
- Handle pending, insufficient, or uncertain cases transparently

The goal of this demo is **integration clarity**, not accuracy guarantees.

---

## 🧩 Verification Marks You’ll See

- Correct  
- Incorrect  
- Verifiable  
- Unverifiable  
- Insufficient  
- Pending  
- AI-Generated  
- Non-AI / Human-Generated  

---

## 🛠 Tech Stack

- React + TypeScript  
- Vite  
- Tailwind CSS  
- `satyamark-react`

---

## ▶️ How the Integration Works (Basic)

### Initialize
```tsx
init({
  app_id: "APP123",
  user_id: "user123"
});
```

### Process content
```tsx
const jobId = await process(domElement, uniqueContentId);
```

### Show status
```tsx
registerStatus(jobId, domElement);
```

```html
<div data-satyamark-status-container></div>
```

---

## 🚀 Run Locally

```bash
git clone <your-repo-url>
cd Frontend/DemoMedia
npm install
npm run dev
```

Open: http://localhost:5173

---

## ⚠️ Notes

- Image verification is experimental
- Video/audio not supported yet
- Results are best-effort, not guarantees

---

**Demo project showing real-world usage of `satyamark-react`**
