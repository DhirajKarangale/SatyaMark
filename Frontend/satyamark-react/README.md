# satyamark-react

> Real-time content verification library for React applications

SatyaMark is a React library that provides real-time verification for
text and image content through AI-powered fact-checking and deepfake
detection. It injects transparent trust signals directly into your UI so
users can distinguish between reliable and unreliable information.

![npm downloads](https://img.shields.io/npm/dt/satyamark-react) [![npm
version](https://badge.fury.io/js/satyamark-react.svg)](https://www.npmjs.com/package/satyamark-react)
[![License:
MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

------------------------------------------------------------------------

## Installation

``` bash
npm install satyamark-react
```

**Peer Dependency:** React 18+

------------------------------------------------------------------------

## Quick Start

### 1. Initialize Connection

``` tsx
import { useEffect } from "react";
import { init } from "satyamark-react";

function App() {
  useEffect(() => {
    init({
      app_id: "your-app-id",
      user_id: "unique-user-id", // Use stable unique user id
    });
  }, []);

  return <YourAppContent />;
}
```

### Optional: onConnected

`onConnected` notifies when the connection state changes.

Callback receives:

    {
      app_id: string;
      user_id: string;
    }

If disconnected or closed, it receives `null`.

``` tsx
import { useEffect } from "react";
import { init, onConnected } from "satyamark-react";

function App() {
  useEffect(() => {
    init({
      app_id: "my-app",
      user_id: "user_123",
    });

    const unsubscribe = onConnected((connection) => {
      if (connection) {
        console.log("Connected:", connection.app_id, connection.user_id);
      } else {
        console.log("Disconnected");
      }
    });

    return unsubscribe;
  }, []);

  return <YourApp />;
}
```

### 2. Process a Content Element

``` tsx
import { useRef, useEffect } from "react";
import { process } from "satyamark-react";

function PostCard({ post }) {
  const ref = useRef(null);

  useEffect(() => {
    if (!cardRef.current) return;
    try {
      process(cardRef.current, postData.id);
    } catch (error) {
      console.log(error);
    }
  }, [post.id]);

  return (
    <div ref={ref}>
      <p>{post.text}</p>
      {post.image && <img src={post.image} alt="" />}

      <div data-satyamark-status-container />
    </div>
  );
}
```

You can style the `data-satyamark-status-container` element according to
your UI requirements.

------------------------------------------------------------------------

## Core Concepts

SatyaMark consists of three core modules that work together:

### 1. Connection Layer

-   Authenticates with your `app_id` and `user_id`
-   Maintains persistent WebSocket connection
-   Handles incoming verification results

### 2. Processing Layer

-   Walks the DOM tree to extract visible text
-   Finds and validates images
-   Sends content to verification service
-   Internally tracks verification jobs

### 3. Status Layer

-   Automatically injects verification icons into your UI
-   Updates status in real-time
-   Provides tooltips on hover
-   Makes icons clickable for detailed results

### Lifecycle Flow

    1. init()      → Establish connection
    2. render      → Display content normally
    3. process()   → Extract content & auto-inject verification status

All retries, result handling, and UI updates are managed internally.

<p align="center">
  <img src="https://raw.githubusercontent.com/DhirajKarangale/SatyaMark/main/Assets/NpmCover/NpmCover_1.png" alt="SatyaMark Architecture" width="100%" />
</p>

------------------------------------------------------------------------

## API Reference

### 1. init(connectionData)

  Establishes WebSocket connection.

  **Parameters**

  -   `app_id: string` — Unique identifier for your application
  -   `user_id: string` — Unique identifier for the current user

### 2. onConnected(callback)

  Listens for connection state changes.

  Callback receives:

      {
        app_id: string;
        user_id: string;
      }

  Returns `null` if disconnected.

### 3. process(rootElement, dataId)

  Extracts text and images from a DOM element and submits them for
  verification.

  **Parameters**

  -   `rootElement: HTMLElement` — DOM element containing the content
  -   `dataId: string` — Unique identifier for this specific content item

------------------------------------------------------------------------

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

------------------------------------------------------------------------

## Best Practices

### Do

-   Initialize `init()` once in your root App component
-   Use a unique and stable `user_id` when calling `init()`
-   Use a stable and unique `dataId` for each content item (database IDs recommended)
-   Call `process()` only after the element is mounted
-   Include `data-satyamark-status-container` where you want status displayed
-   Style the `data-satyamark-status-container` element as per your UI requirements
-   Optionally use `onConnected()` if your UI depends on connection readiness
-   Let SatyaMark manage verification lifecycle and retries internally

### Don't

-   Don't call `init()` multiple times or in multiple components
-   Don't use random or changing `user_id` values for the same user session
-   Don't use random or changing `dataId` values for the same content
-   Don't manually retry `process()` in loops
-   Don't call `process()` before the element exists in the DOM

### Performance Tips

-   **Debounce Input Changes** - Avoid re-processing content on every keystroke
-   **Process Visible Content Only** - Use Intersection Observer for large feeds
-   **Prevent Re-Render Loops** - Ensure process() isn’t triggered repeatedly by state updates
-   **Use Stable Content Identifiers** - Prevent duplicate or unnecessary verification calls

------------------------------------------------------------------------

## Troubleshooting

### 1. Invalid root element

  **Cause:** Calling `process()` with null/undefined ref.

  **Solution:** Check ref exists before processing:
  ```tsx
  if (!cardRef.current) return;
  try {
    process(cardRef.current, postData.id);
  } catch (error) {
    console.log(error);
  }
  ```

### 2. No valid text or image found

  **Cause:** Element contains no extractable content or all images fail to load.

  **Solution:** Ensure content has visible text (3+ chars) or valid image URLs.

### 3. Status icon not appearing

  **Cause:** Missing `data-satyamark-status-container` or `process()` not executed.

  **Solution:** Ensure:

    - `init()` was called
    - `process()` ran after the element mounted
    - `data-satyamark-status-container` exists inside the processed element

### 4. Connection fails or times out

  **Cause:** Network issues, invalid credentials, or server unavailable.

  **Solution:** Check console for WebSocket errors. Verify `app_id` and `user_id` are correct.

### 5. Verification stuck on "Pending"

  **Cause:** Server processing delay.

  **Solution:** Verification can take a few seconds to a few minutes depending on content complexity and system load.

------------------------------------------------------------------------

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

------------------------------------------------------------------------

## License

MIT © SatyaMark Contributors