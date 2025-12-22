# satyamark-react

> Real-time content verification library for React applications

SatyaMark is a React library that provides real-time verification for text and image content through AI-powered fact-checking and deepfake detection. Display transparent trust signals directly in your UI to help users distinguish between reliable and unreliable information.

[![npm version](https://badge.fury.io/js/satyamark-react.svg)](https://www.npmjs.com/package/satyamark-react)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Features

- ✅ **Real-time verification** of text content through fact-checking APIs
- 🤖 **AI-generated media detection** for images
- 🔄 **Live status updates** via WebSocket connection
- 🎨 **Automatic UI injection** with verification marks
- ⚡ **Lightweight integration** - minimal code required
- 🔗 **Interactive results** - click through to detailed evidence
- 📱 **Framework agnostic** - works with any React setup

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)
- [Verification Marks](#verification-marks)
- [Troubleshooting](#troubleshooting)
- [Limitations](#limitations)
- [Contributing](#contributing)

## Installation

Install via npm or yarn:

```bash
npm install satyamark-react
```

```bash
yarn add satyamark-react
```

**Peer Dependencies:**
- React 18+ (compatible with React 19)

## Quick Start

### 1. Initialize Connection

Call `init()` once when your app loads to establish the WebSocket connection:

```tsx
import { useEffect } from "react";
import { init } from "satyamark-react";

function App() {
  useEffect(() => {
    init({
      app_id: "your-app-id",
      user_id: "unique-user-id",
    });
  }, []);

  return <YourAppContent />;
}
```

### 2. Create a Verified Component

```tsx
import { useRef, useEffect, useState } from "react";
import { process, registerStatus } from "satyamark-react";

function PostCard({ post }) {
  const contentRef = useRef(null);
  const [jobId, setJobId] = useState(null);

  // Process content after render
  useEffect(() => {
    if (!contentRef.current) return;

    process(contentRef.current, post.id)
      .then(setJobId)
      .catch(console.error);
  }, [post.id]);

  // Register status display
  useEffect(() => {
    if (!jobId || !contentRef.current) return;
    registerStatus(jobId, contentRef.current);
  }, [jobId]);

  return (
    <div ref={contentRef}>
      <p>{post.text}</p>
      {post.image && <img src={post.image} alt="Post" />}
      
      {/* Verification mark appears here */}
      <div data-satyamark-status-container />
    </div>
  );
}
```

That's it! The verification mark will automatically appear and update.

## Core Concepts

<p align="center">
  <img src="https://raw.githubusercontent.com/DhirajKarangale/SatyaMark/main/Assets/NpmCover/NpmCover_1.png" alt="SatyaMark Architecture" width="90%" />
</p>

SatyaMark consists of three core modules that work together:

### 1. Connection Layer (`satyamark_connect`)

Manages the WebSocket connection to the verification server.

- Authenticates with your `app_id` and `user_id`
- Maintains persistent connection
- Handles incoming verification results
- Supports connection callbacks

### 2. Processing Layer (`satyamark_process`)

Extracts content from rendered DOM elements for verification.

- Walks the DOM tree to extract all visible text
- Finds and validates images
- Sends content to verification service
- Returns a unique `jobId` for tracking

### 3. Status Layer (`satyamark_status_controller`)

Manages visual display of verification status.

- Injects verification icons into your UI
- Updates status in real-time
- Provides tooltips on hover
- Makes icons clickable for detailed results

### Lifecycle Flow

```
1. init()          → Establish connection
2. render          → Display content normally
3. process()       → Extract and send for verification
4. registerStatus() → Attach status display
5. Auto-update     → Marks appear and update automatically
```

## API Reference

### Connection API

#### `init(connectionData, options?)`

Establishes WebSocket connection to the SatyaMark server.

**Parameters:**
- `connectionData` (SatyaMarkConnectionData) - **Required**
  - `app_id` (string): Your application's unique identifier
  - `user_id` (string): Current user's unique identifier
- `options` (object) - Optional
  - `onConnected` (function): Callback when connection succeeds

**Returns:** `void`

**Example:**
```tsx
init({
  app_id: "my-social-app",
  user_id: "user_12345",
});
```

#### `onConnected(callback)`

Register a callback for when the connection is established.

**Parameters:**
- `callback` (ConnectedCallback): Function receiving connection data

**Returns:** `void`

**Example:**
```tsx
onConnected((data) => {
  console.log("Connected:", data);
});
```

#### `onReceive(callback)`

Subscribe to incoming verification updates. Used internally by status controller.

**Parameters:**
- `callback` (ReceiveCallback): Function receiving verification data

**Returns:** Unsubscribe function

---

### Processing API

#### `process(divRef, dataId)`

Extracts content from a DOM element and submits for verification.

**Parameters:**
- `divRef` (HTMLDivElement): The DOM element containing content
- `dataId` (string): Unique identifier for this content (e.g., post ID)

**Returns:** `Promise<string>` - Resolves with `jobId` for tracking

**Throws:**
- `"Invalid root element"` - if divRef is null/undefined
- `"dataId is required"` - if dataId is empty
- `"No valid text or image found"` - if element has no content
- `"Extracted text is too short"` - if text is less than 3 characters

**Example:**
```tsx
process(ref.current, "post_123")
  .then((jobId) => registerStatus(jobId, ref.current))
  .catch((error) => console.error(error.message));
```

---

### Status API

#### `registerStatus(jobId, rootElement, options?)`

Registers a DOM element to display verification status.

**Parameters:**
- `jobId` (string): Job ID returned from `process()`
- `rootElement` (HTMLElement): Element containing status container
- `options` (StatusOptions) - Optional
  - `iconSize` (number): Icon size in pixels (default: 20)

**Returns:** `void`

**Requirements:**
- Root element must contain a child with `data-satyamark-status-container` attribute

**Example:**
```tsx
registerStatus(jobId, contentRef.current, {
  iconSize: 24,
});
```

**HTML Structure:**
```tsx
<div ref={contentRef}>
  {/* Your content */}
  <div data-satyamark-status-container />
</div>
```

## Usage Examples

### Basic Setup

```tsx
import { useEffect } from "react";
import { init, onConnected } from "satyamark-react";

function App() {
  useEffect(() => {
    init({
      app_id: "my-app",
      user_id: getCurrentUserId(),
    });

    onConnected((data) => {
      console.log("SatyaMark connected:", data);
    });
  }, []);

  return <div>{/* Your app */}</div>;
}
```

### Complete Component with Error Handling

```tsx
import { useRef, useEffect, useState } from "react";
import { process, registerStatus } from "satyamark-react";

function VerifiedPost({ post }) {
  const contentRef = useRef(null);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!contentRef.current) return;

    setStatus("processing");

    process(contentRef.current, post.id)
      .then((jobId) => {
        setStatus("success");
        registerStatus(jobId, contentRef.current);
      })
      .catch((err) => {
        setStatus("error");
        setError(err.message);
      });
  }, [post.id]);

  return (
    <div ref={contentRef} className="post-card">
      <div className="content">
        <p>{post.text}</p>
        {post.image && <img src={post.image} alt="" />}
      </div>

      {status === "success" && (
        <div data-satyamark-status-container />
      )}

      {status === "error" && (
        <div className="error-badge">{error}</div>
      )}
    </div>
  );
}
```

### List of Posts

```tsx
function PostFeed({ posts }) {
  return (
    <div className="feed">
      {posts.map((post) => (
        <VerifiedPost key={post.id} post={post} />
      ))}
    </div>
  );
}
```

### Custom Icon Size

```tsx
useEffect(() => {
  if (!jobId || !ref.current) return;

  registerStatus(jobId, ref.current, {
    iconSize: 32, // Larger icon
  });
}, [jobId]);
```

## Best Practices

### ✅ Do

- **Initialize once** at app startup in your root component
- **Use unique dataIds** for each piece of content (post ID, comment ID, etc.)
- **Process after render** - ensure content exists in DOM before calling `process()`
- **Handle errors gracefully** - short or empty content will throw errors
- **Use refs correctly** - pass actual DOM elements, not null
- **Test with real content** - minimum 3 characters or valid image required

### ❌ Don't

- **Don't call init() multiple times** - creates duplicate connections
- **Don't process before render** - ref.current will be null
- **Don't reuse dataIds** - each content piece needs unique identifier
- **Don't forget status container** - `data-satyamark-status-container` is required
- **Don't manually update icons** - library handles it automatically
- **Don't process empty content** - ensure content exists first

### ⚡ Performance Tips

- **Debounce rapid updates** - don't re-process on every keystroke
- **Process only visible content** - use Intersection Observer for long lists
- **Cache jobIds** - avoid re-processing identical content
- **Lazy load verification** - process when content enters viewport

## Verification Marks

SatyaMark displays different marks based on verification results:

| Mark | Meaning |
|------|---------|
| ✅ **Verifiable** | Content contains factual claims that can be verified |
| ❌ **Unverifiable** | Cannot be verified (opinions, random data, etc.) |
| ⚠️ **Insufficient** | Verifiable but not enough reliable sources available |
| ✔️ **Correct** | Factually correct based on evidence |
| ❗ **Incorrect** | Factually incorrect or contradicts sources |
| ⏳ **Pending** | Verification in progress |
| 🤖 **AI-Generated** | Media appears to be AI-generated |
| 👤 **Human-Generated** | Media appears to be human-created |
| ❓ **Uncertain** | Cannot confidently determine AI vs human origin |

**Interactive:** After verification completes, clicking the mark opens a detailed results page with sources and evidence.

## Troubleshooting

### "Invalid root element"

**Cause:** Calling `process()` with null/undefined ref.

**Solution:** Check ref exists before processing:
```tsx
if (!contentRef.current) return;
process(contentRef.current, post.id);
```

### "No valid text or image found"

**Cause:** Element contains no extractable content or all images fail to load.

**Solution:** Ensure content has visible text (3+ chars) or valid image URLs.

### Status icon not appearing

**Cause:** Missing `data-satyamark-status-container` or `registerStatus()` not called.

**Solution:** Add status container and call `registerStatus()` with correct jobId:
```tsx
<div data-satyamark-status-container />
// ...
registerStatus(jobId, contentRef.current);
```

### Connection fails or times out

**Cause:** Network issues, invalid credentials, or server unavailable.

**Solution:** Check console for WebSocket errors. Verify `app_id` and `user_id` are correct.

### Multiple verification requests

**Cause:** useEffect dependency array causing re-renders.

**Solution:** Use stable identifiers in dependency array:
```tsx
useEffect(() => {
  // Process logic
}, [post.id]); // Stable dependency
```

### Verification stuck on "Pending"

**Cause:** Server processing or jobId mismatch.

**Solution:** Verification can take 5-30 seconds. Ensure jobId is correctly passed to `registerStatus()`.

## Limitations

SatyaMark is actively developed. Current limitations:

- **Minimum content:** Text must be at least 3 characters
- **Single image:** Only first valid image is processed per element
- **No offline support:** Requires active WebSocket connection
- **No local caching:** Content sent to server every time (caching planned)
- **Single connection:** Multiple tabs share connection state
- **Limited retry logic:** Manual refresh required if connection drops
- **No client rate limiting:** Apps should implement own throttling

These are being addressed in future releases. Check the [GitHub repository](https://github.com/DhirajKarangale/SatyaMark) for updates.

## Contributing

SatyaMark is fully open-source and welcomes contributions!

### How to Contribute

- **Report bugs** on [GitHub Issues](https://github.com/DhirajKarangale/SatyaMark/issues)
- **Request features** that align with the project's mission
- **Improve documentation** - submit PRs for clarity improvements
- **Contribute code** - follow the contributing guidelines in the repository
- **Share feedback** on library design and API

### Project Links

- **Main Repository:** [github.com/DhirajKarangale/SatyaMark](https://github.com/DhirajKarangale/SatyaMark)
- **npm Package:** [npmjs.com/package/satyamark-react](https://www.npmjs.com/package/satyamark-react)
- **Demo Application:** [Live Demo](https://satyamark.vercel.app)

All contributions are reviewed for alignment with SatyaMark's principles: transparency, evidence-based verification, and accessibility.

## License

MIT © SatyaMark Contributors

---

**Need help?** Open an issue on [GitHub](https://github.com/DhirajKarangale/SatyaMark) or check the [live demo](https://satyamark.vercel.app) for examples.
