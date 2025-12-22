import { memo, useState, useEffect } from "react";
import { motion, type Variants } from "framer-motion";
import GradientText from "../reactbits/GradientText/GradientText";
import { MARK_META } from "../utils/MARK_META";

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 14 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.08 * i, duration: 0.4, ease: "easeOut" },
  }),
};

function Documentation() {
  const url_git_main = import.meta.env.VITE_URL_GIT_MAIN;
  const url_git_demo = import.meta.env.VITE_URL_GIT_DEMO;
  const url_live_demo = import.meta.env.VITE_URL_LIVE_DEMO;
  const url_npm_library = import.meta.env.VITE_URL_NPM_LIBRARY;

  const [showScrollTop, setShowScrollTop] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 300);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen w-full bg-transparent px-4 md:px-8 py-10">
      <motion.div
        initial="hidden"
        animate="visible"
        className="max-w-5xl mx-auto flex flex-col gap-12 text-gray-300"
      >
        {/* HERO */}
        <motion.section custom={0} variants={fadeUp}>
          <GradientText
            colors={["#40ffaa", "#4079ff", "#40ffaa"]}
            animationSpeed={6}
            showBorder={false}
            className="text-4xl md:text-5xl font-semibold"
          >
            Documentation
          </GradientText>

          <p className="mt-4 text-lg leading-relaxed max-w-3xl">
            Complete guide to integrating <span className="text-cyan-400 font-semibold">satyamark-react</span> into your React application.
            This library provides real-time content verification for text and images, surfacing transparent trust signals directly in your UI.
          </p>
        </motion.section>

        {/* WHAT IS SATYAMARK */}
        <motion.section custom={1} variants={fadeUp} className="space-y-3">
          <h2 className="text-white text-2xl font-semibold">
            What is SatyaMark?
          </h2>

          <p className="leading-relaxed">
            SatyaMark is a React library that connects your application to a centralized, AI-powered verification service.
            It helps users distinguish between reliable and unreliable content in real-time by displaying verification marks next to posts, comments, or any rendered content.
          </p>

          <div className="bg-white/5 border border-white/15 rounded-xl p-5 space-y-2">
            <h3 className="text-white font-semibold">Key Features</h3>
            <ul className="list-disc pl-5 space-y-1">
              <li>Real-time verification of text and image content</li>
              <li>Automatic AI-generated media detection</li>
              <li>Fact-checking with evidence-backed verdicts</li>
              <li>Non-intrusive, lightweight integration</li>
              <li>Live status updates via WebSocket</li>
              <li>Works with any rendered HTML content</li>
            </ul>
          </div>

          <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-xl p-5 space-y-2">
            <h3 className="text-cyan-400 font-semibold">Real-World Use Cases</h3>
            <ul className="list-disc pl-5 space-y-1 text-gray-300">
              <li>Social media platforms verifying posts and comments</li>
              <li>News aggregators checking article credibility</li>
              <li>Community forums detecting misinformation</li>
              <li>E-commerce platforms verifying product claims</li>
              <li>Educational platforms validating study materials</li>
            </ul>
          </div>
        </motion.section>

        {/* INSTALLATION */}
        <motion.section custom={2} variants={fadeUp} className="space-y-3">
          <h2 className="text-white text-2xl font-semibold">
            Installation
          </h2>

          <p className="text-gray-400">
            Install the library using npm or yarn:
          </p>

          <pre className="bg-white/5 border border-white/15 rounded-xl p-4 text-sm overflow-x-auto">
            <code>npm install satyamark-react</code>
          </pre>

          <pre className="bg-white/5 border border-white/15 rounded-xl p-4 text-sm overflow-x-auto">
            <code>yarn add satyamark-react</code>
          </pre>

          <div className="text-sm text-gray-400 mt-2">
            <strong className="text-gray-300">Peer Dependencies:</strong> React 18+ (works with React 19)
          </div>

          <div className="text-sm text-gray-400">
            <strong className="text-gray-300">npm Package:</strong>{" "}
            <a
              href={url_npm_library}
              target="_blank"
              rel="noopener noreferrer"
              className="text-cyan-400 underline"
            >
              satyamark-react
            </a>
          </div>
        </motion.section>

        {/* ARCHITECTURE */}
        <motion.section custom={3} variants={fadeUp} className="space-y-4">
          <h2 className="text-white text-2xl font-semibold">
            High-Level Architecture
          </h2>

          <p className="text-gray-400">
            The library consists of three core modules that work together to provide seamless verification:
          </p>

          <div className="space-y-4">
            <div className="bg-white/5 border border-white/15 rounded-xl p-5">
              <h3 className="text-white font-semibold text-lg mb-2">
                1️⃣ Connection Layer (satyamark_connect)
              </h3>
              <p className="text-gray-400 mb-2">
                Establishes and manages a persistent WebSocket connection to the SatyaMark verification server.
              </p>
              <ul className="list-disc pl-5 space-y-1 text-sm text-gray-400">
                <li>Handles authentication with app_id and user_id</li>
                <li>Sends content for verification</li>
                <li>Receives real-time status updates</li>
                <li>Manages connection lifecycle and reconnection</li>
              </ul>
            </div>

            <div className="bg-white/5 border border-white/15 rounded-xl p-5">
              <h3 className="text-white font-semibold text-lg mb-2">
                2️⃣ Processing Layer (satyamark_process)
              </h3>
              <p className="text-gray-400 mb-2">
                Extracts visible content from rendered DOM elements and submits it for verification.
              </p>
              <ul className="list-disc pl-5 space-y-1 text-sm text-gray-400">
                <li>Traverses the DOM to extract all visible text</li>
                <li>Finds and validates images within the element</li>
                <li>Generates unique job IDs for tracking</li>
                <li>Handles validation and error cases</li>
              </ul>
            </div>

            <div className="bg-white/5 border border-white/15 rounded-xl p-5">
              <h3 className="text-white font-semibold text-lg mb-2">
                3️⃣ Status Layer (satyamark_status_controller)
              </h3>
              <p className="text-gray-400 mb-2">
                Manages the visual display of verification marks and provides interactive UI updates.
              </p>
              <ul className="list-disc pl-5 space-y-1 text-sm text-gray-400">
                <li>Renders verification icons dynamically</li>
                <li>Updates status as verification progresses</li>
                <li>Provides tooltips and click-through to detailed results</li>
                <li>Automatically injects visual elements into your UI</li>
              </ul>
            </div>
          </div>

          <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-5">
            <h3 className="text-blue-400 font-semibold mb-2">Lifecycle Flow</h3>
            <ol className="list-decimal pl-5 space-y-2 text-gray-300">
              <li><strong>Connect:</strong> Initialize connection when your app loads</li>
              <li><strong>Render:</strong> Display content normally in your React components</li>
              <li><strong>Process:</strong> Extract and send content to verification service</li>
              <li><strong>Register:</strong> Attach status container to receive live updates</li>
              <li><strong>Update:</strong> Verification marks appear and update automatically</li>
            </ol>
          </div>
        </motion.section>

        {/* API DOCUMENTATION */}
        <motion.section custom={4} variants={fadeUp} className="space-y-4">
          <h2 className="text-white text-2xl font-semibold">
            API Documentation
          </h2>

          {/* CONNECTION API */}
          <div className="space-y-3">
            <h3 className="text-white text-xl font-semibold">
              Connection API (satyamark_connect)
            </h3>

            <div className="bg-white/5 border border-white/15 rounded-xl p-5 space-y-4">
              <div>
                <h4 className="text-cyan-400 font-mono text-sm mb-2">
                  init(connectionData, options?)
                </h4>
                <p className="text-gray-400 text-sm mb-3">
                  Establishes a WebSocket connection to the SatyaMark server. Call this once when your app initializes.
                </p>
                <div className="bg-black/30 rounded-lg p-3 space-y-2 text-sm">
                  <div>
                    <span className="text-purple-400">Parameters:</span>
                    <ul className="list-disc pl-5 mt-1 space-y-1">
                      <li>
                        <code className="text-cyan-300">connectionData</code>
                        <span className="text-gray-400"> (SatyaMarkConnectionData): Required</span>
                        <ul className="list-circle pl-5 mt-1">
                          <li><code className="text-cyan-300">app_id</code>: Your application's unique identifier</li>
                          <li><code className="text-cyan-300">user_id</code>: Current user's unique identifier</li>
                        </ul>
                      </li>
                      <li>
                        <code className="text-cyan-300">options</code>
                        <span className="text-gray-400"> (object): Optional</span>
                        <ul className="list-circle pl-5 mt-1">
                          <li><code className="text-cyan-300">onConnected</code>: Callback function when connection succeeds</li>
                        </ul>
                      </li>
                    </ul>
                  </div>
                  <div>
                    <span className="text-purple-400">Returns:</span>
                    <span className="text-gray-400"> void</span>
                  </div>
                  <div>
                    <span className="text-purple-400">Side Effects:</span>
                    <ul className="list-disc pl-5 mt-1 space-y-1 text-gray-400">
                      <li>Creates global WebSocket connection</li>
                      <li>Stores connection data for subsequent operations</li>
                      <li>Prevents duplicate connections if already connected</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-cyan-400 font-mono text-sm mb-2">
                  onConnected(callback)
                </h4>
                <p className="text-gray-400 text-sm mb-3">
                  Register a callback to execute when WebSocket connection is successfully established.
                </p>
                <div className="bg-black/30 rounded-lg p-3 space-y-2 text-sm">
                  <div>
                    <span className="text-purple-400">Parameters:</span>
                    <ul className="list-disc pl-5 mt-1">
                      <li>
                        <code className="text-cyan-300">callback</code>
                        <span className="text-gray-400"> (ConnectedCallback): Function receiving connectionData</span>
                      </li>
                    </ul>
                  </div>
                  <div>
                    <span className="text-purple-400">Returns:</span>
                    <span className="text-gray-400"> void</span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-cyan-400 font-mono text-sm mb-2">
                  onReceive(callback)
                </h4>
                <p className="text-gray-400 text-sm mb-3">
                  Subscribe to incoming verification updates from the server. Used internally by the status controller.
                </p>
                <div className="bg-black/30 rounded-lg p-3 space-y-2 text-sm">
                  <div>
                    <span className="text-purple-400">Parameters:</span>
                    <ul className="list-disc pl-5 mt-1">
                      <li>
                        <code className="text-cyan-300">callback</code>
                        <span className="text-gray-400"> (ReceiveCallback): Function receiving verification data</span>
                      </li>
                    </ul>
                  </div>
                  <div>
                    <span className="text-purple-400">Returns:</span>
                    <span className="text-gray-400"> Function to unsubscribe</span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-cyan-400 font-mono text-sm mb-2">
                  sendData(text, image_url, dataId)
                </h4>
                <p className="text-gray-400 text-sm mb-3">
                  Internal function that sends content to the verification server. Use <code className="text-cyan-300">process()</code> instead.
                </p>
                <div className="bg-black/30 rounded-lg p-3 space-y-2 text-sm">
                  <div>
                    <span className="text-purple-400">Parameters:</span>
                    <ul className="list-disc pl-5 mt-1 space-y-1">
                      <li><code className="text-cyan-300">text</code>: Extracted text content (min 3 chars)</li>
                      <li><code className="text-cyan-300">image_url</code>: Valid image URL or empty string</li>
                      <li><code className="text-cyan-300">dataId</code>: Unique identifier for the content</li>
                    </ul>
                  </div>
                  <div>
                    <span className="text-purple-400">Returns:</span>
                    <span className="text-gray-400"> string (jobId) - Unique identifier for tracking this verification job</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* PROCESSING API */}
          <div className="space-y-3">
            <h3 className="text-white text-xl font-semibold">
              Processing API (satyamark_process)
            </h3>

            <div className="bg-white/5 border border-white/15 rounded-xl p-5 space-y-4">
              <div>
                <h4 className="text-cyan-400 font-mono text-sm mb-2">
                  process(divRef, dataId)
                </h4>
                <p className="text-gray-400 text-sm mb-3">
                  Core function that extracts content from a DOM element and submits it for verification. This is the primary function you'll use.
                </p>
                <div className="bg-black/30 rounded-lg p-3 space-y-2 text-sm">
                  <div>
                    <span className="text-purple-400">Parameters:</span>
                    <ul className="list-disc pl-5 mt-1 space-y-1">
                      <li>
                        <code className="text-cyan-300">divRef</code>
                        <span className="text-gray-400"> (HTMLDivElement): The DOM element containing content to verify</span>
                      </li>
                      <li>
                        <code className="text-cyan-300">dataId</code>
                        <span className="text-gray-400"> (string): Unique identifier for this content (e.g., post ID)</span>
                      </li>
                    </ul>
                  </div>
                  <div>
                    <span className="text-purple-400">Returns:</span>
                    <span className="text-gray-400"> Promise&lt;string&gt; - Resolves with jobId for tracking</span>
                  </div>
                  <div>
                    <span className="text-purple-400">Throws:</span>
                    <ul className="list-disc pl-5 mt-1 space-y-1 text-gray-400">
                      <li>"Invalid root element" - if divRef is null/undefined</li>
                      <li>"dataId is required" - if dataId is empty</li>
                      <li>"No valid text or image found" - if element contains no verifiable content</li>
                      <li>"Extracted text is too short" - if text is less than 3 characters</li>
                    </ul>
                  </div>
                  <div>
                    <span className="text-purple-400">Behavior:</span>
                    <ul className="list-disc pl-5 mt-1 space-y-1 text-gray-400">
                      <li>Walks the DOM tree to extract all visible text nodes</li>
                      <li>Finds all img elements and validates their URLs</li>
                      <li>Returns the first valid image found</li>
                      <li>Merges extracted text with commas</li>
                      <li>Requires either valid text (3+ chars) or valid image</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4 text-sm">
              <strong className="text-yellow-400">Important:</strong>
              <span className="text-gray-300"> Always call </span>
              <code className="text-cyan-300">process()</code>
              <span className="text-gray-300"> after the content is fully rendered in the DOM. Use refs and useEffect to ensure timing is correct.</span>
            </div>
          </div>

          {/* STATUS API */}
          <div className="space-y-3">
            <h3 className="text-white text-xl font-semibold">
              Status API (satyamark_status_controller)
            </h3>

            <div className="bg-white/5 border border-white/15 rounded-xl p-5 space-y-4">
              <div>
                <h4 className="text-cyan-400 font-mono text-sm mb-2">
                  registerStatus(jobId, rootElement, options?)
                </h4>
                <p className="text-gray-400 text-sm mb-3">
                  Registers a DOM element to display live verification status updates. Must contain a child element with <code className="text-cyan-300">data-satyamark-status-container</code> attribute.
                </p>
                <div className="bg-black/30 rounded-lg p-3 space-y-2 text-sm">
                  <div>
                    <span className="text-purple-400">Parameters:</span>
                    <ul className="list-disc pl-5 mt-1 space-y-1">
                      <li>
                        <code className="text-cyan-300">jobId</code>
                        <span className="text-gray-400"> (string): Job ID returned from process()</span>
                      </li>
                      <li>
                        <code className="text-cyan-300">rootElement</code>
                        <span className="text-gray-400"> (HTMLElement): Element containing status container</span>
                      </li>
                      <li>
                        <code className="text-cyan-300">options</code>
                        <span className="text-gray-400"> (StatusOptions): Optional configuration</span>
                        <ul className="list-circle pl-5 mt-1">
                          <li><code className="text-cyan-300">iconSize</code>: Size in pixels (default: 20)</li>
                        </ul>
                      </li>
                    </ul>
                  </div>
                  <div>
                    <span className="text-purple-400">Returns:</span>
                    <span className="text-gray-400"> void</span>
                  </div>
                  <div>
                    <span className="text-purple-400">Side Effects:</span>
                    <ul className="list-disc pl-5 mt-1 space-y-1 text-gray-400">
                      <li>Immediately displays "pending" icon</li>
                      <li>Injects img element into status container</li>
                      <li>Creates tooltip element for hover interaction</li>
                      <li>Automatically updates when verification completes</li>
                      <li>Makes icon clickable when verification finishes (links to detailed results)</li>
                    </ul>
                  </div>
                  <div>
                    <span className="text-purple-400">Required HTML Structure:</span>
                    <pre className="bg-black/50 rounded p-2 mt-2 text-cyan-300 overflow-x-auto">
                      {`<div ref={containerRef}>
  {/* Your content */}
  <div data-satyamark-status-container />
</div>`}
                    </pre>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4 text-sm">
              <strong className="text-green-400">Automatic Updates:</strong>
              <span className="text-gray-300"> Once registered, the status controller automatically listens for verification results and updates the icon. You don't need to manually poll or update.</span>
            </div>
          </div>
        </motion.section>

        {/* USAGE EXAMPLES */}
        <motion.section custom={5} variants={fadeUp} className="space-y-4">
          <h2 className="text-white text-2xl font-semibold">
            Usage Examples
          </h2>

          <div className="space-y-4">
            <div>
              <h3 className="text-white text-lg font-semibold mb-3">
                Basic Setup (App Initialization)
              </h3>
              <pre className="bg-white/5 border border-white/15 rounded-xl p-4 text-sm overflow-x-auto">
                <code>{`import { useEffect } from "react";
import { init, onConnected } from "satyamark-react";

function App() {
  useEffect(() => {
    // Initialize connection once when app loads
    init({
      app_id: "my-social-app",
      user_id: "user_12345",
    });

    // Optional: Listen for connection success
    onConnected((data) => {
      console.log("SatyaMark connected:", data);
    });
  }, []);

  return <YourAppContent />;
}`}</code>
              </pre>
            </div>

            <div>
              <h3 className="text-white text-lg font-semibold mb-3">
                Complete Component Example
              </h3>
              <pre className="bg-white/5 border border-white/15 rounded-xl p-4 text-sm overflow-x-auto">
                <code>{`import { useRef, useEffect, useState } from "react";
import { process, registerStatus } from "satyamark-react";

interface Post {
  id: string;
  text: string;
  imageUrl?: string;
}

function PostCard({ post }: { post: Post }) {
  const contentRef = useRef<HTMLDivElement>(null);
  const [jobId, setJobId] = useState<string | null>(null);

  // Step 1: Process content after render
  useEffect(() => {
    if (!contentRef.current) return;

    process(contentRef.current, post.id)
      .then((newJobId) => {
        setJobId(newJobId);
      })
      .catch((error) => {
        console.error("Verification failed:", error.message);
      });
  }, [post.id]);

  // Step 2: Register status display when jobId is ready
  useEffect(() => {
    if (!jobId || !contentRef.current) return;

    registerStatus(jobId, contentRef.current, {
      iconSize: 24, // Optional: customize icon size
    });
  }, [jobId]);

  return (
    <div ref={contentRef} className="post-card">
      {/* Content to verify */}
      <div className="post-content">
        <p>{post.text}</p>
        {post.imageUrl && <img src={post.imageUrl} alt="Post" />}
      </div>

      {/* Status container - icon appears here */}
      <div className="verification-badge">
        <div data-satyamark-status-container />
      </div>
    </div>
  );
}`}</code>
              </pre>
            </div>

            <div>
              <h3 className="text-white text-lg font-semibold mb-3">
                Error Handling Example
              </h3>
              <pre className="bg-white/5 border border-white/15 rounded-xl p-4 text-sm overflow-x-auto">
                <code>{`function VerifiedContent({ post }: { post: Post }) {
  const contentRef = useRef<HTMLDivElement>(null);
  const [verificationState, setVerificationState] = useState<
    "idle" | "processing" | "success" | "error"
  >("idle");
  const [errorMessage, setErrorMessage] = useState<string>("");

  useEffect(() => {
    if (!contentRef.current) return;

    setVerificationState("processing");

    process(contentRef.current, post.id)
      .then((jobId) => {
        setVerificationState("success");
        registerStatus(jobId, contentRef.current!);
      })
      .catch((error) => {
        setVerificationState("error");
        
        // Handle specific errors
        if (error.message.includes("too short")) {
          setErrorMessage("Content too short to verify");
        } else if (error.message.includes("No valid")) {
          setErrorMessage("No verifiable content found");
        } else {
          setErrorMessage("Verification unavailable");
        }
      });
  }, [post.id]);

  return (
    <div ref={contentRef}>
      <div className="post-content">{post.text}</div>
      
      {verificationState === "success" && (
        <div data-satyamark-status-container />
      )}
      
      {verificationState === "error" && (
        <div className="error-badge">{errorMessage}</div>
      )}
    </div>
  );
}`}</code>
              </pre>
            </div>

            <div>
              <h3 className="text-white text-lg font-semibold mb-3">
                Multiple Posts / List Example
              </h3>
              <pre className="bg-white/5 border border-white/15 rounded-xl p-4 text-sm overflow-x-auto">
                <code>{`function PostFeed({ posts }: { posts: Post[] }) {
  return (
    <div className="feed">
      {posts.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
}

// Each PostCard automatically processes and displays
// its own verification status independently`}</code>
              </pre>
            </div>
          </div>
        </motion.section>

        {/* BEST PRACTICES */}
        <motion.section custom={6} variants={fadeUp} className="space-y-3">
          <h2 className="text-white text-2xl font-semibold">
            Best Practices
          </h2>

          <div className="space-y-3">
            <div className="bg-white/5 border border-white/15 rounded-xl p-5">
              <h3 className="text-green-400 font-semibold mb-2">✅ Do</h3>
              <ul className="list-disc pl-5 space-y-2 text-gray-300">
                <li>
                  <strong>Initialize once</strong> at app startup, not per component
                </li>
                <li>
                  <strong>Use unique dataIds</strong> for each piece of content (post ID, comment ID, etc.)
                </li>
                <li>
                  <strong>Process after render</strong> - ensure content is in the DOM before calling process()
                </li>
                <li>
                  <strong>Handle errors gracefully</strong> - verification may fail for short or empty content
                </li>
                <li>
                  <strong>Place status container</strong> where it makes sense visually (corner, below content, etc.)
                </li>
                <li>
                  <strong>Use refs correctly</strong> - pass the actual DOM element, not null
                </li>
                <li>
                  <strong>Test with real content</strong> - minimum 3 characters of text or valid image
                </li>
              </ul>
            </div>

            <div className="bg-white/5 border border-white/15 rounded-xl p-5">
              <h3 className="text-red-400 font-semibold mb-2">❌ Don't</h3>
              <ul className="list-disc pl-5 space-y-2 text-gray-300">
                <li>
                  <strong>Don't call init() multiple times</strong> - it creates duplicate connections
                </li>
                <li>
                  <strong>Don't process before render</strong> - ref.current will be null
                </li>
                <li>
                  <strong>Don't reuse dataIds</strong> - each content piece needs a unique identifier
                </li>
                <li>
                  <strong>Don't forget the status container</strong> - registerStatus() requires <code className="text-cyan-300">data-satyamark-status-container</code>
                </li>
                <li>
                  <strong>Don't manually update icons</strong> - the library handles it automatically
                </li>
                <li>
                  <strong>Don't process empty divs</strong> - ensure content exists before processing
                </li>
                <li>
                  <strong>Don't block render</strong> - verification happens asynchronously
                </li>
              </ul>
            </div>

            <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-xl p-5">
              <h3 className="text-cyan-400 font-semibold mb-2">⚡ Performance Tips</h3>
              <ul className="list-disc pl-5 space-y-2 text-gray-300">
                <li>
                  <strong>Debounce rapid updates</strong> - don't re-process on every keystroke if content is editable
                </li>
                <li>
                  <strong>Process only visible content</strong> - use Intersection Observer for long lists
                </li>
                <li>
                  <strong>Cache jobIds</strong> - store them to avoid re-processing identical content
                </li>
                <li>
                  <strong>Lazy load verification</strong> - process content when it enters viewport
                </li>
              </ul>
            </div>
          </div>
        </motion.section>

        {/* VERIFICATION MARKS */}
        <motion.section custom={7} variants={fadeUp} className="space-y-4">
          <h2 className="text-white text-2xl font-semibold">
            Verification Marks Reference
          </h2>

          <p className="text-gray-400">
            SatyaMark displays different marks based on the verification result. These are automatically updated by the status controller:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.values(MARK_META).map((mark, i) => (
              <motion.div
                key={mark.label}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 * i }}
                className="bg-white/5 border border-white/15 backdrop-blur-sm rounded-xl px-4 py-3 flex flex-col gap-2"
              >
                <div className="flex items-center gap-3">
                  <img
                    src={mark.icon}
                    alt={mark.label}
                    className="w-6 h-6 object-contain"
                  />
                  <span className={`font-medium ${mark.color}`}>
                    {mark.label}
                  </span>
                </div>

                <p className="text-sm text-gray-400 leading-snug">
                  {mark.description}
                </p>
              </motion.div>
            ))}
          </div>

          <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 text-sm">
            <strong className="text-blue-400">Interactive Marks:</strong>
            <span className="text-gray-300"> After verification completes, clicking the icon opens a detailed results page with sources and confidence scores.</span>
          </div>
        </motion.section>

        {/* TROUBLESHOOTING */}
        <motion.section custom={8} variants={fadeUp} className="space-y-3">
          <h2 className="text-white text-2xl font-semibold">
            Common Mistakes & Troubleshooting
          </h2>

          <div className="space-y-3">
            <div className="bg-white/5 border border-white/15 rounded-xl p-5">
              <h3 className="text-red-400 font-semibold mb-2">
                ❌ "Invalid root element"
              </h3>
              <p className="text-gray-400 mb-2">
                <strong>Cause:</strong> Calling process() before the ref is attached or with null/undefined.
              </p>
              <p className="text-gray-300">
                <strong>Solution:</strong> Ensure useEffect runs after render and check if ref.current exists:
              </p>
              <pre className="bg-black/30 rounded p-3 mt-2 text-sm overflow-x-auto">
                <code className="text-cyan-300">{`if (!contentRef.current) return;
process(contentRef.current, post.id);`}</code>
              </pre>
            </div>

            <div className="bg-white/5 border border-white/15 rounded-xl p-5">
              <h3 className="text-red-400 font-semibold mb-2">
                ❌ "No valid text or image found"
              </h3>
              <p className="text-gray-400 mb-2">
                <strong>Cause:</strong> The element contains no extractable content or all images fail to load.
              </p>
              <p className="text-gray-300">
                <strong>Solution:</strong> Verify your content has visible text or valid image URLs. Don't process empty divs.
              </p>
            </div>

            <div className="bg-white/5 border border-white/15 rounded-xl p-5">
              <h3 className="text-red-400 font-semibold mb-2">
                ❌ Status icon not appearing
              </h3>
              <p className="text-gray-400 mb-2">
                <strong>Cause:</strong> Missing <code className="text-cyan-300">data-satyamark-status-container</code> attribute or registerStatus() not called.
              </p>
              <p className="text-gray-300">
                <strong>Solution:</strong> Add the status container element and ensure registerStatus() receives the correct jobId:
              </p>
              <pre className="bg-black/30 rounded p-3 mt-2 text-sm overflow-x-auto">
                <code className="text-cyan-300">{`<div data-satyamark-status-container />
// ...
registerStatus(jobId, contentRef.current);`}</code>
              </pre>
            </div>

            <div className="bg-white/5 border border-white/15 rounded-xl p-5">
              <h3 className="text-red-400 font-semibold mb-2">
                ❌ Connection fails or times out
              </h3>
              <p className="text-gray-400 mb-2">
                <strong>Cause:</strong> Network issues, invalid credentials, or server unavailable.
              </p>
              <p className="text-gray-300">
                <strong>Solution:</strong> Check console for WebSocket errors. Verify app_id and user_id are correct. The library logs connection status.
              </p>
            </div>

            <div className="bg-white/5 border border-white/15 rounded-xl p-5">
              <h3 className="text-red-400 font-semibold mb-2">
                ❌ Multiple verification requests for same content
              </h3>
              <p className="text-gray-400 mb-2">
                <strong>Cause:</strong> useEffect dependency array causing re-renders or missing cleanup.
              </p>
              <p className="text-gray-300">
                <strong>Solution:</strong> Add dataId/postId to dependency array and use stable identifiers:
              </p>
              <pre className="bg-black/30 rounded p-3 mt-2 text-sm overflow-x-auto">
                <code className="text-cyan-300">{`useEffect(() => {
  // Process logic
}, [post.id]); // Stable dependency`}</code>
              </pre>
            </div>

            <div className="bg-white/5 border border-white/15 rounded-xl p-5">
              <h3 className="text-yellow-400 font-semibold mb-2">
                ⚠️ Verification stuck on "Pending"
              </h3>
              <p className="text-gray-400 mb-2">
                <strong>Cause:</strong> Server is processing or jobId mismatch between process() and registerStatus().
              </p>
              <p className="text-gray-300">
                <strong>Solution:</strong> Verification can take 5-30 seconds. If it persists, check that jobId is correctly passed to registerStatus().
              </p>
            </div>
          </div>
        </motion.section>

        {/* LIMITATIONS */}
        <motion.section custom={9} variants={fadeUp} className="space-y-3">
          <h2 className="text-white text-2xl font-semibold">
            Current Limitations & Known Issues
          </h2>

          <div className="bg-orange-500/10 border border-orange-500/30 rounded-xl p-5 space-y-3">
            <p className="text-gray-300 leading-relaxed">
              SatyaMark is actively developed and continuously improving. Here are current limitations:
            </p>

            <ul className="list-disc pl-5 space-y-2 text-gray-300">
              <li>
                <strong>Minimum content requirement:</strong> Text must be at least 3 characters. Very short content cannot be verified.
              </li>
              <li>
                <strong>Image validation:</strong> Only the first valid image in an element is processed. Multiple images are not yet supported.
              </li>
              <li>
                <strong>No offline support:</strong> Requires active WebSocket connection. Offline verification is not available.
              </li>
              <li>
                <strong>No local caching:</strong> Every content piece is sent to the server. Client-side caching is planned.
              </li>
              <li>
                <strong>Single connection per user:</strong> Multiple tabs/windows share the same connection state.
              </li>
              <li>
                <strong>Limited retry logic:</strong> Connection drops are not automatically retried. Manual page refresh required.
              </li>
              <li>
                <strong>No rate limiting on client:</strong> Apps should implement their own throttling for rapid content changes.
              </li>
            </ul>

            <p className="text-gray-400 text-sm italic mt-4">
              These limitations are being addressed in future releases. Check the GitHub repository for roadmap and updates.
            </p>
          </div>
        </motion.section>

        {/* OPEN SOURCE */}
        <motion.section custom={10} variants={fadeUp} className="space-y-3">
          <h2 className="text-white text-2xl font-semibold">
            Open Source & Contributing
          </h2>

          <p className="leading-relaxed">
            SatyaMark is a fully open-source project designed to combat misinformation through transparent, verifiable trust signals.
            We welcome contributions from the community.
          </p>

          <div className="bg-white/5 border border-white/15 rounded-xl p-5 space-y-3">
            <h3 className="text-white font-semibold">Project Links</h3>
            <ul className="list-disc pl-5 space-y-1 text-gray-400">
              <li>
                Main Repository:{" "}
                <a
                  href={url_git_main}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-cyan-400 underline"
                >
                  github.com/DhirajKarangale/SatyaMark
                </a>
              </li>
              <li>
                npm Package:{" "}
                <a
                  href={url_npm_library}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-cyan-400 underline"
                >
                  satyamark-react
                </a>
              </li>
              <li>
                Demo Application:{" "}
                <a
                  href={url_git_demo}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-cyan-400 underline"
                >
                  DemoMedia (GitHub)
                </a>
              </li>
              <li>
                Live Demo:{" "}
                <a
                  href={url_live_demo}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-cyan-400 underline"
                >
                  Try SatyaMark
                </a>
              </li>
            </ul>
          </div>

          <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-5 space-y-3">
            <h3 className="text-green-400 font-semibold">How to Contribute</h3>
            <ul className="list-disc pl-5 space-y-2 text-gray-300">
              <li>
                <strong>Report bugs or issues</strong> on the GitHub Issues page
              </li>
              <li>
                <strong>Submit feature requests</strong> that align with SatyaMark's mission
              </li>
              <li>
                <strong>Improve documentation</strong> - this page is open for PRs
              </li>
              <li>
                <strong>Contribute code</strong> - review the contributing guidelines in the repo
              </li>
              <li>
                <strong>Share feedback</strong> on library design and API improvements
              </li>
            </ul>
          </div>

          <p className="text-gray-400 italic">
            All contributions are reviewed and aligned with SatyaMark's principles: transparency, evidence-based verification, and accessibility.
          </p>
        </motion.section>

        {/* FOOTER */}
        <motion.section
          custom={11}
          variants={fadeUp}
          className="pt-6 border-t border-white/10 text-center space-y-2"
        >
          <p className="text-gray-400">
            Need help? Found an issue? Have suggestions?
          </p>
          <p className="text-gray-300">
            Open an issue on{" "}
            <a
              href={url_git_main}
              target="_blank"
              rel="noopener noreferrer"
              className="text-cyan-400 underline"
            >
              GitHub
            </a>{" "}
            or check the{" "}
            <a
              href={url_live_demo}
              target="_blank"
              rel="noopener noreferrer"
              className="text-cyan-400 underline"
            >
              live demo
            </a>{" "}
            for examples.
          </p>
        </motion.section>
      </motion.div>

      {/* Scroll to Top Button */}
      {showScrollTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-6 right-6 z-50 bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/50 hover:border-cyan-400 backdrop-blur-sm rounded-full p-3 transition-all duration-200 hover:scale-110 shadow-lg"
          aria-label="Scroll to top"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6 text-cyan-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 10l7-7m0 0l7 7m-7-7v18"
            />
          </svg>
        </button>
      )}
    </div>
  );
}

export default memo(Documentation);
