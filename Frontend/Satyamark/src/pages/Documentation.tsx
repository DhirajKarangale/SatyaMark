import { memo, useState, useEffect } from "react";
import { motion, type Variants } from "framer-motion";
import { Link } from "react-router-dom";
import {
  BookOpen, Code, Package, Github, ExternalLink,
  CheckCircle, Terminal, FileCode, Zap
} from "lucide-react";
import { MARK_META } from "../utils/MARK_META";
import { routeChat } from "../utils/Routes";

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.1 * i, duration: 0.5, ease: "easeOut" }
  })
};

function Documentation() {
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

  const CodeBlock = ({ code }: { code: string; language?: string }) => (
    <pre className="bg-slate-900 border border-white/10 rounded-xl p-4 overflow-x-auto">
      <code className="text-sm text-gray-300">{code}</code>
    </pre>
  );

  return (
    <div className="min-h-screen bg-slate-950 text-gray-100">
      {/* Hero Section */}
      <section className="bg-linear-to-b from-slate-900 to-slate-950 border-b border-white/10">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <motion.div
            initial="hidden"
            animate="visible"
            className="space-y-6"
          >
            <motion.div custom={0} variants={fadeUp}>
              <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">
                Documentation
              </h1>
              <p className="text-xl text-gray-400 max-w-3xl">
                Complete guide to integrating SatyaMark verification into your React application
              </p>
            </motion.div>

            <motion.div custom={1} variants={fadeUp} className="flex flex-wrap gap-4">
              <a
                href="https://www.npmjs.com/package/satyamark-react"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 
                                    bg-gradient-to-r from-cyan-600 to-blue-600 
                                    hover:from-cyan-500 hover:to-blue-500
                                    text-white font-semibold rounded-lg 
                                    shadow-lg shadow-cyan-500/25 transition-all"
              >
                <Package size={18} />
                View on NPM
              </a>
              <a
                href="https://github.com/DhirajKarangale/SatyaMark"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 
                                    bg-white/5 hover:bg-white/10 
                                    border border-white/20 
                                    text-white font-semibold rounded-lg transition-all"
              >
                <Github size={18} />
                GitHub Repo
              </a>
              <a
                href="https://satyamark-demo-socialmedia.vercel.app/"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 
                                    bg-white/5 hover:bg-white/10 
                                    border border-white/20 
                                    text-white font-semibold rounded-lg transition-all"
              >
                <ExternalLink size={18} />
                Live Demo
              </a>
            </motion.div>

            <motion.div custom={2} variants={fadeUp} className="flex flex-wrap gap-3 pt-2">
              <img
                src="https://img.shields.io/npm/v/satyamark-react?color=22c55e&label=version"
                alt="npm version"
                className="h-5"
              />
              <img
                src="https://img.shields.io/npm/dt/satyamark-react?color=38bdf8&label=total%20downloads"
                alt="npm downloads"
                className="h-5"
              />
              <img
                src="https://img.shields.io/npm/l/satyamark-react?color=818cf8"
                alt="npm license"
                className="h-5"
              />
            </motion.div>
          </motion.div>
        </div>
      </section>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-16">
        {/* What is SatyaMark */}
        <section className="space-y-6">
          <div className="flex items-center gap-3">
            <BookOpen className="text-cyan-400" size={28} />
            <h2 className="text-3xl font-bold text-white">What is SatyaMark?</h2>
          </div>

          <div className="space-y-4">
            <p className="text-lg text-gray-300 leading-relaxed">
              SatyaMark is a React library that provides real-time content verification for text and images.
              It connects your application to a centralized AI-powered verification service that displays
              trust indicators next to content.
            </p>

            <div className="grid sm:grid-cols-2 gap-4">
              <div className="bg-white/5 border border-white/10 rounded-xl p-5 space-y-2">
                <CheckCircle className="text-green-400" size={24} />
                <h3 className="text-white font-semibold">Real-time Verification</h3>
                <p className="text-sm text-gray-400">
                  Instant verification of text and images with live WebSocket updates
                </p>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-xl p-5 space-y-2">
                <Zap className="text-cyan-400" size={24} />
                <h3 className="text-white font-semibold">Easy Integration</h3>
                <p className="text-sm text-gray-400">
                  Simple React hooks and functions for seamless integration
                </p>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-xl p-5 space-y-2">
                <Code className="text-blue-400" size={24} />
                <h3 className="text-white font-semibold">TypeScript Support</h3>
                <p className="text-sm text-gray-400">
                  Full TypeScript definitions for type-safe development
                </p>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-xl p-5 space-y-2">
                <FileCode className="text-purple-400" size={24} />
                <h3 className="text-white font-semibold">Lightweight</h3>
                <p className="text-sm text-gray-400">
                  Minimal bundle size with no heavy dependencies
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Installation */}
        <section className="space-y-6">
          <div className="flex items-center gap-3">
            <Terminal className="text-cyan-400" size={28} />
            <h2 className="text-3xl font-bold text-white">Installation</h2>
          </div>

          <div className="space-y-4">
            <p className="text-gray-300">
              Install the package using npm or yarn:
            </p>

            <div className="space-y-3">
              <div>
                <CodeBlock code="npm install satyamark-react" />
              </div>
            </div>

            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
              <p className="text-sm text-gray-300">
                <strong className="text-blue-400">Requirements:</strong> React 18+ (works with React 19)
              </p>
            </div>
          </div>
        </section>

        {/* Quick Start */}
        <section className="space-y-6">
          <div className="flex items-center gap-3">
            <Zap className="text-cyan-400" size={28} />
            <h2 className="text-3xl font-bold text-white">Quick Start</h2>
          </div>

          <div className="space-y-8">

            {/* Step 1 */}
            <div>
              <h3 className="text-xl font-semibold text-white mb-3">
                1. Initialize SatyaMark
              </h3>

              <p className="text-gray-300 mb-4">
                Initialize SatyaMark once in your root App component.
              </p>

              <CodeBlock code={`import { useEffect } from "react";
import { init } from "satyamark-react";

function App() {
  useEffect(() => {
    init({
      app_id: "your-app-id",
      user_id: "unique-user-id"
    });
  }, []);

  return <YourApp />;
}`} />

              <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 mt-4">
                <p className="text-sm text-gray-300">
                  <strong className="text-blue-400">Optional:</strong> You can use
                  <code className="text-cyan-300"> onConnected()</code> to track
                  connection state and show a loader before rendering your app.
                </p>
              </div>
            </div>

            {/* Optional onConnected Section */}
            <div>
              <h3 className="text-xl font-semibold text-white mb-3">
                Optional: Track Connection Status
              </h3>

              <p className="text-gray-300 mb-4">
                <code className="text-cyan-300"> onConnected()</code> allows you to listen
                for connection readiness. This is completely optional.
              </p>

              <CodeBlock code={`import { useEffect, useState } from "react";
import { init, onConnected } from "satyamark-react";

function App() {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    init({
      app_id: "your-app-id",
      user_id: "unique-user-id"
    });

    const unsubscribe = onConnected((data) => {
      setIsConnected(!!data);
    });

    return unsubscribe;
  }, []);

  if (!isConnected) {
    return <div>Connecting to SatyaMark...</div>;
  }

  return <YourApp />;
}`} />
            </div>

            {/* Step 2 */}
            <div>
              <h3 className="text-xl font-semibold text-white mb-3">
                2. Process a Content Element
              </h3>

              <p className="text-gray-300 mb-4">
                Attach a ref to your content container and call
                <code className="text-cyan-300"> process()</code> once after mount.
                SatyaMark automatically extracts text and images from the element.
              </p>

              <CodeBlock code={`import { useEffect, useRef } from "react";
import { process } from "satyamark-react";

function PostCard({ post }) {
  const ref = useRef(null);

  useEffect(() => {
    if (!ref.current) return;
    process(ref.current, post.id);
  }, []);

  return (
    <div ref={ref}>
      <h3>{post.title}</h3>
      <img src={post.imageURL} alt="post" />
      <p>{post.description}</p>

      {/* Status renders automatically here */}
      <div data-satyamark-status-container />
    </div>
  );
}`} />
            </div>

            {/* Step 3 */}
            <div>
              <h3 className="text-xl font-semibold text-white mb-3">
                3. Automatic Status Rendering
              </h3>

              <p className="text-gray-300 mb-4">
                SatyaMark automatically injects verification status inside any element
                containing the attribute below:
              </p>

              <CodeBlock code={`data-satyamark-status-container`} />

              <p className="text-sm text-gray-400 mt-3">
                No manual status handling is required.
                Verification lifecycle, retries, and rendering are managed internally.
              </p>
            </div>

          </div>
        </section>

        {/* Core Concepts */}
        <section className="space-y-6">
          <div className="flex items-center gap-3">
            <Code className="text-cyan-400" size={28} />
            <h2 className="text-3xl font-bold text-white">Core Concepts</h2>
          </div>

          <div className="space-y-6 text-gray-300 leading-relaxed">

            <div>
              <h3 className="text-xl font-semibold text-white mb-2">
                1. Connection Layer
              </h3>
              <ul className="space-y-2 text-sm">
                <li>• Authenticates with your app_id and user_id</li>
                <li>• Maintains persistent WebSocket connection</li>
                <li>• Handles incoming verification results</li>
              </ul>
            </div>

            <div>
              <h3 className="text-xl font-semibold text-white mb-2">
                2. Processing Layer
              </h3>
              <ul className="space-y-2 text-sm">
                <li>• Walks the DOM tree to extract visible text</li>
                <li>• Detects and validates images</li>
                <li>• Submits content for verification</li>
              </ul>
            </div>

            <div>
              <h3 className="text-xl font-semibold text-white mb-2">
                3. Status Layer
              </h3>
              <ul className="space-y-2 text-sm">
                <li>• Automatically injects verification icons</li>
                <li>• Updates status in real-time</li>
                <li>• Displays tooltips and detailed results</li>
              </ul>
            </div>

            <div className="bg-white/5 border border-white/10 rounded-xl p-4">
              <h4 className="text-white font-semibold mb-2">Lifecycle Flow</h4>
              <CodeBlock
                code={`1. init()      → Establish connection
2. render      → Display content
3. process()   → Extract & auto-inject verification status`}
              />
              <p className="text-sm text-gray-400 mt-3">
                All retries, result handling, and UI updates are managed internally.
              </p>
            </div>

          </div>
        </section>

        {/* API Reference */}
        <section className="space-y-6">
          <div className="flex items-center gap-3">
            <Terminal className="text-cyan-400" size={28} />
            <h2 className="text-3xl font-bold text-white">API Reference</h2>
          </div>

          <div className="space-y-8 text-gray-300">

            {/* init */}
            <div className="bg-white/5 border border-white/10 rounded-xl p-5 space-y-3">
              <h3 className="text-white font-semibold text-lg">init(connectionData)</h3>
              <p className="text-sm">
                Establishes WebSocket connection.
              </p>
              <ul className="text-sm space-y-1">
                <li>• <code>app_id: string</code> — Unique identifier for your application</li>
                <li>• <code>user_id: string</code> — Unique identifier for the current user</li>
              </ul>
            </div>

            {/* onConnected */}
            <div className="bg-white/5 border border-white/10 rounded-xl p-5 space-y-3">
              <h3 className="text-white font-semibold text-lg">onConnected(callback)</h3>
              <p className="text-sm">
                Listens for connection state changes.
              </p>
              <CodeBlock
                code={`{
  app_id: string;
  user_id: string;
}`}
              />
              <p className="text-sm text-gray-400">
                Returns null if disconnected.
              </p>
            </div>

            {/* process */}
            <div className="bg-white/5 border border-white/10 rounded-xl p-5 space-y-3">
              <h3 className="text-white font-semibold text-lg">process(rootElement, dataId)</h3>
              <p className="text-sm">
                Extracts text and images from a DOM element and submits them for verification.
              </p>
              <ul className="text-sm space-y-1">
                <li>• <code>rootElement: HTMLElement</code> — DOM element containing content</li>
                <li>• <code>dataId: string</code> — Unique identifier for this content</li>
              </ul>
            </div>

          </div>
        </section>

        {/* Verification Marks */}
        <section className="space-y-6">
          <div className="flex items-center gap-3">
            <CheckCircle className="text-cyan-400" size={28} />
            <h2 className="text-3xl font-bold text-white">Verification Marks</h2>
          </div>

          <p className="text-gray-300">
            SatyaMark assigns the following verification marks based on content analysis:
          </p>

          <div className="grid sm:grid-cols-2 gap-4">
            {Object.values(MARK_META).map((mark) => (
              <div
                key={mark.label}
                className="bg-white/5 border border-white/10 rounded-xl p-4 space-y-3"
              >
                <div className="flex items-center gap-3">
                  <img
                    src={mark.icon}
                    alt={mark.label}
                    className="w-7 h-7 object-contain"
                  />
                  <span className={`font-semibold text-lg ${mark.color}`}>
                    {mark.label}
                  </span>
                </div>
                <p className="text-sm text-gray-400 leading-relaxed">
                  {mark.description}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* Best Practices */}
        <section className="space-y-6">
          <div className="flex items-center gap-3">
            <CheckCircle className="text-cyan-400" size={28} />
            <h2 className="text-3xl font-bold text-white">Best Practices</h2>
          </div>

          <div className="space-y-4">
            <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-5">
              <h3 className="text-green-400 font-semibold mb-2">✓ Do</h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>• Initialize init() once in your root App component</li>
                <li>• Use a unique and stable user_id when calling init()</li>
                <li>• Use stable and unique content IDs (database IDs recommended)</li>
                <li>• Call process() only after the element is mounted</li>
                <li>• Include data-satyamark-status-container where you want status displayed</li>
                <li>• Style the data-satyamark-status-container element as per your UI requirements</li>
                <li>• Optionally use onConnected() if your UI depends on connection readiness</li>
                <li>• Let SatyaMark handle lifecycle and retries internally</li>
              </ul>
            </div>

            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-5">
              <h3 className="text-red-400 font-semibold mb-2">✗ Don't</h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>• Don't call init() multiple times or in multiple components</li>
                <li>• Don't use random or changing user_id values for the same user session</li>
                <li>• Don't use random IDs for the same content</li>
                <li>• Don't manually retry process() in loops</li>
                <li>• Don't call process() before the element exists in the DOM</li>
              </ul>
            </div>

            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-5">
              <h3 className="text-blue-400 font-semibold mb-2">⚡ Performance Tips</h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>• <strong>Debounce Input Changes</strong> — Avoid re-processing content on every keystroke</li>
                <li>• <strong>Process Visible Content Only</strong> — Use Intersection Observer for large feeds</li>
                <li>• <strong>Prevent Re-Render Loops</strong> — Ensure process() isn’t triggered repeatedly by state updates</li>
                <li>• <strong>Use Stable Content Identifiers</strong> — Prevent duplicate or unnecessary verification calls</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Troubleshooting */}
        <section className="space-y-6">
          <div className="flex items-center gap-3">
            <CheckCircle className="text-cyan-400" size={28} />
            <h2 className="text-3xl font-bold text-white">Troubleshooting</h2>
          </div>

          <div className="space-y-6 text-gray-300 text-sm">

            <div>
              <h3 className="text-white font-semibold mb-1">
                Invalid root element
              </h3>
              <p className="text-gray-400">
                <strong>Cause:</strong> <code>process()</code> was called before the DOM element was mounted.
              </p>
              <p className="text-gray-400 mt-1">
                <strong>Solution:</strong> Ensure the ref exists before calling <code>process()</code>.
              </p>
            </div>

            <div>
              <h3 className="text-white font-semibold mb-1">
                No valid text or image found
              </h3>
              <p className="text-gray-400">
                <strong>Cause:</strong> The element contains no extractable content.
              </p>
              <p className="text-gray-400 mt-1">
                <strong>Solution:</strong> Ensure the content contains at least 3 characters of text or a valid image.
              </p>
            </div>

            <div>
              <h3 className="text-white font-semibold mb-1">
                Status not appearing
              </h3>
              <p className="text-gray-400">
                <strong>Cause:</strong> Verification lifecycle was not properly triggered.
              </p>
              <ul className="space-y-1 mt-2 text-gray-400">
                <li>• Ensure <code>init()</code> was called</li>
                <li>• Ensure <code>process()</code> ran after mount</li>
                <li>• Ensure <code>data-satyamark-status-container</code> exists</li>
              </ul>
            </div>

            <div>
              <h3 className="text-white font-semibold mb-1">
                Connection fails or times out
              </h3>
              <p className="text-gray-400">
                <strong>Cause:</strong> Network issues, invalid credentials, or server unavailability.
              </p>
              <p className="text-gray-400 mt-1">
                <strong>Solution:</strong> Check the browser console for WebSocket errors and verify
                <code> app_id </code> and <code> user_id </code> are valid and stable.
              </p>
            </div>

            <div>
              <h3 className="text-white font-semibold mb-1">
                Verification stuck on Pending
              </h3>
              <p className="text-gray-400">
                <strong>Cause:</strong> Server processing delay.
              </p>
              <p className="text-gray-400 mt-1">
                <strong>Solution:</strong> Verification can take a few seconds to a few minutes depending on content complexity and system load.
              </p>
            </div>

          </div>
        </section>

        {/* Resources */}
        <section className="space-y-6">
          <div className="flex items-center gap-3">
            <ExternalLink className="text-cyan-400" size={28} />
            <h2 className="text-3xl font-bold text-white">Additional Resources</h2>
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            <a
              href="https://www.npmjs.com/package/satyamark-react"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white/5 hover:bg-white/10 border border-white/10 
                                rounded-xl p-5 transition-all group"
            >
              <Package className="text-cyan-400 mb-3" size={24} />
              <h3 className="text-white font-semibold mb-2 group-hover:text-cyan-400 transition-colors">
                NPM Package
              </h3>
              <p className="text-sm text-gray-400">
                View package details, versions, and download stats
              </p>
            </a>

            <a
              href="https://github.com/DhirajKarangale/SatyaMark"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white/5 hover:bg-white/10 border border-white/10 
                                rounded-xl p-5 transition-all group"
            >
              <Github className="text-cyan-400 mb-3" size={24} />
              <h3 className="text-white font-semibold mb-2 group-hover:text-cyan-400 transition-colors">
                GitHub Repository
              </h3>
              <p className="text-sm text-gray-400">
                Full source code, issues, and contribution guidelines
              </p>
            </a>

            <a
              href="https://satyamark-demo-socialmedia.vercel.app/"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white/5 hover:bg-white/10 border border-white/10 
                                rounded-xl p-5 transition-all group"
            >
              <ExternalLink className="text-cyan-400 mb-3" size={24} />
              <h3 className="text-white font-semibold mb-2 group-hover:text-cyan-400 transition-colors">
                Live Demo
              </h3>
              <p className="text-sm text-gray-400">
                See SatyaMark in action with a social media example
              </p>
            </a>

            <Link
              to={routeChat}
              className="bg-white/5 hover:bg-white/10 border border-white/10 
                                rounded-xl p-5 transition-all group"
            >
              <Zap className="text-cyan-400 mb-3" size={24} />
              <h3 className="text-white font-semibold mb-2 group-hover:text-cyan-400 transition-colors">
                Try it Now
              </h3>
              <p className="text-sm text-gray-400">
                Test verification with our interactive demo
              </p>
            </Link>
          </div>
        </section>

        {/* Support */}
        <section className="space-y-6">
          <div className="flex items-center gap-3">
            <BookOpen className="text-cyan-400" size={28} />
            <h2 className="text-3xl font-bold text-white">Support</h2>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-xl p-6 space-y-4">
            <p className="text-gray-300">
              Have questions or need help? We're here to assist:
            </p>

            <div className="space-y-3">
              <div>
                <div className="text-sm text-gray-400 mb-1">Email</div>
                <a
                  href="mailto:dhirajkarangale02@gmail.com"
                  className="text-cyan-400 hover:text-cyan-300"
                >
                  dhirajkarangale02@gmail.com
                </a>
              </div>

              <div>
                <div className="text-sm text-gray-400 mb-1">GitHub Issues</div>
                <a
                  href="https://github.com/DhirajKarangale/SatyaMark/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-cyan-400 hover:text-cyan-300"
                >
                  Report bugs or request features
                </a>
              </div>

              <div>
                <div className="text-sm text-gray-400 mb-1">Developer</div>
                <div className="flex gap-4">
                  <a
                    href="https://dhirajkarangale.netlify.app/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-cyan-400 hover:text-cyan-300"
                  >
                    Portfolio
                  </a>
                  <a
                    href="https://www.linkedin.com/in/dhiraj-karangale-464ab91bb/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-cyan-400 hover:text-cyan-300"
                  >
                    LinkedIn
                  </a>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* Scroll to Top Button */}
      {showScrollTop && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={scrollToTop}
          className="fixed bottom-8 right-8 w-12 h-12 rounded-full 
                        bg-gradient-to-r from-cyan-600 to-blue-600 
                        hover:from-cyan-500 hover:to-blue-500
                        text-white shadow-lg shadow-cyan-500/25 
                        flex items-center justify-center transition-all z-40"
        >
          ↑
        </motion.button>
      )}
    </div>
  );
}

export default memo(Documentation);
