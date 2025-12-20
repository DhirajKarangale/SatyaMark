# SatyaMark

SatyaMark is a centralized, AI-powered content verification platform that helps users and platforms understand the credibility of digital content through transparent, evidence-backed verification results.

SatyaMark is built as trust infrastructure, not a fact-checking authority.

---

## Live Deployment

SatyaMark is live and publicly accessible:

- **Live URL:** https://satyamark.vercel.app/

Users can manually verify content, inspect verification results, and view detailed reasoning by opening verification links shared from external platforms.

---

## Project Scope & Purpose

SatyaMark provides a centralized verification layer where digital content can be verified, inspected, and explained in a transparent and consistent manner.

The project enables:

- Manual verification of text and images
- Deep inspection of verification results using a shared verification ID
- Clear explanations showing why a specific verification mark was assigned
- Confidence scores that communicate uncertainty honestly
- Source references when available
- Re-verification requests when users disagree with a result
- A single, neutral place to view verification context across different platforms
- Built-in documentation explaining how SatyaMark works and how to use it

This allows SatyaMark to function as a common credibility reference point for the internet.

---

## Core Capabilities

### Manual Verification

Users can submit:
- Text
- Images

Each verification produces:
- A verification mark
- A confidence score
- A human-readable explanation
- Sources, when available

---

### Centralized Verification Viewing

SatyaMark is designed for cross-platform usage.

External platforms (such as social media or messaging apps) can display a verification mark.  
When a user clicks that mark, they are routed using a verification ID and can inspect:

- Full reasoning behind the verdict
- How the decision was reached
- Confidence and uncertainty details
- Supporting sources

---

### Re-Verification & Feedback

If users believe a verification is incorrect or incomplete, they can request re-verification.

This feedback loop helps improve accuracy and system behavior over time.

---

## Supported Verification Types

### Active

- Text verification – most reliable
- Image verification – experimental, lower confidence

### Planned

- Video verification
- Audio verification
- Hybrid multi-signal verification

SatyaMark follows an incremental rollout strategy and avoids overpromising accuracy.

---

## Verification Marks

SatyaMark assigns clear, visual trust indicators:

- Correct
- Incorrect
- Verifiable
- Unverifiable
- Insufficient
- Pending
- AI-Generated
- Non-AI / Human-Generated

These marks are designed to be instantly understandable and consistent across platforms.

---

## Verification Flow

1. Content is submitted (text or image)
2. Claims or signals are extracted
3. Cross-verification is performed using:
   - Retrieval-augmented generation (RAG)
   - Trusted external sources
   - Internal knowledge bases
   - AI-generation detection signals
4. A verification mark, confidence score, and explanation are generated
5. Users can inspect results and request re-verification

Transparency is prioritized over false certainty.

---

## Documentation

SatyaMark includes built-in documentation explaining:

- How verification works internally
- How users can submit content
- How to interpret verification marks and confidence scores
- How platforms should integrate and display SatyaMark responsibly
- Best practices for handling uncertainty

The documentation is intended for both developers and general users.

---

## Running SatyaMark Locally

### 1. Clone the Project

```bash
git clone <your-repo-url>
```

### 2. Navigate to the Frontend

```bash
cd .\Frontend\Satyamark\
```

### 3. Create Environment File

Create a `.env` file in `Frontend/Satyamark` with the following values:

```env
VITE_URL_BASE=<backend_base_url>
VITE_URL_WS=<backend_websocket_url>

VITE_CLOUD_NAME=<cloudinary_cloud_name>
VITE_UPLOAD_PRESET=<cloudinary_upload_preset>
```

### 4. Install Dependencies

```bash
npm install
```

### 5. Run in Development Mode

```bash
npm run dev
```

---

## Privacy & Data Handling

SatyaMark is privacy-first by design.

- No advertising, profiling, or data resale
- Original text is not permanently stored
- A short AI-generated summary may be stored for transparency
- Images may be temporarily stored only to display verification results
- Data is processed ephemerally wherever possible

---

## Platform Architecture

- Central verification backend
- Real-time job processing and updates
- ID-based verification retrieval
- SDK and API–friendly integration model
- Modular and extensible design

---

## Important Constraints

- SatyaMark is not infallible
- Image verification accuracy is currently limited
- Video and audio verification are not yet supported
- Confidence scores reflect uncertainty, not absolute truth

---

## Design Principles

- Transparency over certainty
- Trust before speed
- Privacy-first by default
- Honest accuracy disclosure
- Incremental and scalable rollout

---

## Summary

SatyaMark provides a centralized, transparent mechanism for verifying digital content and exposing the reasoning, confidence, and sources behind each verification outcome.
