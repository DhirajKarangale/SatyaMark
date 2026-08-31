# SatyaMark Demo – Social Media Use Case

A demo social media application showcasing how **SatyaMark** can be integrated into real-world platforms using the **`satyamark-react`** library to verify text and image content in real time.

This project demonstrates how credibility signals (trust marks, confidence, explanations) can be embedded directly into user-generated content feeds.

---

## 🌐 Live Demo

👉 **Live URL:**  
<a href="https://satyamark-demo-socialmedia.vercel.app/" target="_blank" rel="noopener noreferrer">
  https://satyamark-demo-socialmedia.vercel.app/
</a>

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

## 🚀 Run Locally (Full-Stack Evaluation)

*Ensure you have configured the Backend and AI workers as described in the main repository's Reproduction Guide.*

```bash
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

## 🤝 Open Source & Contributing

SatyaMark is proudly open-source. We welcome contributions to this demo app and the core library.

- Check out the [Contributing Guide](../../CONTRIBUTING.md) to get started.
- Review our [Code of Conduct](../../CODE_OF_CONDUCT.md).
- Found a bug or have an idea? [Open an issue on GitHub](https://github.com/DhirajKarangale/SatyaMark/issues).

---

**Demo project showing real-world usage of `satyamark-react`**
