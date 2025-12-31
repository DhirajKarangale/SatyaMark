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

  const CodeBlock = ({ code, language = "typescript" }: { code: string; language?: string }) => (
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
                <div className="text-sm text-gray-400 mb-2">npm</div>
                <CodeBlock code="npm install satyamark-react" />
              </div>
              <div>
                <div className="text-sm text-gray-400 mb-2">yarn</div>
                <CodeBlock code="yarn add satyamark-react" />
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

          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-semibold text-white mb-3">1. Initialize Connection</h3>
              <p className="text-gray-300 mb-4">
                First, establish a WebSocket connection when your app loads:
              </p>
              <CodeBlock code={`import { useEffect } from "react";
import { init } from "satyamark-react";

function App() {
  useEffect(() => {
    init({
      app_id: "your-app-name",
      user_id: "user-unique-id"
    });
  }, []);

  return <YourAppContent />;
}`} />
            </div>

            <div>
              <h3 className="text-xl font-semibold text-white mb-3">2. Verify Text Content</h3>
              <p className="text-gray-300 mb-4">
                Submit text for verification and display the result:
              </p>
              <CodeBlock code={`import { useState } from "react";
import { process } from "satyamark-react";

function VerifyText() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);

  const handleVerify = async () => {
    try {
      const jobId = await process(
        text,           // Text to verify
        "",             // No image
        "unique-id-1"   // Unique content ID
      );
      console.log("Verification job started:", jobId);
    } catch (error) {
      console.error("Verification failed:", error);
    }
  };

  return (
    <div>
      <textarea 
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter text to verify..."
      />
      <button onClick={handleVerify}>
        Verify Content
      </button>
    </div>
  );
}`} />
            </div>

            <div>
              <h3 className="text-xl font-semibold text-white mb-3">3. Verify Images</h3>
              <p className="text-gray-300 mb-4">
                Submit an image URL for AI generation detection:
              </p>
              <CodeBlock code={`import { process } from "satyamark-react";

async function verifyImage(imageUrl: string) {
  try {
    const jobId = await process(
      "",              // No text
      imageUrl,        // Image URL to verify
      "unique-id-2"    // Unique content ID
    );
    console.log("Image verification started:", jobId);
  } catch (error) {
    console.error("Verification failed:", error);
  }
}`} />
            </div>

            <div>
              <h3 className="text-xl font-semibold text-white mb-3">4. Listen for Results</h3>
              <p className="text-gray-300 mb-4">
                Subscribe to verification results in real-time:
              </p>
              <CodeBlock code={`import { useEffect } from "react";
import { onReceive } from "satyamark-react";

function ResultListener() {
  useEffect(() => {
    const unsubscribe = onReceive((result) => {
      console.log("Verification result:", result);
      // result contains: jobId, mark, confidence, reason, urls
    });

    return unsubscribe; // Cleanup on unmount
  }, []);

  return <div>Listening for results...</div>;
}`} />
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

        {/* Result Object */}
        <section className="space-y-6">
          <div className="flex items-center gap-3">
            <Code className="text-cyan-400" size={28} />
            <h2 className="text-3xl font-bold text-white">Verification Result Object</h2>
          </div>

          <p className="text-gray-300">
            When verification completes, you'll receive a result object with the following structure:
          </p>

          <CodeBlock code={`{
  jobId: string;           // Unique job identifier
  dataId: string;          // Your content ID
  mark: string;            // Verification mark (e.g., "correct", "ai", etc.)
  confidence: number;      // Confidence score (0-100)
  reason: string;          // Detailed explanation
  urls?: string[];         // Supporting source URLs (if available)
  type?: "text" | "image"; // Content type
  summary?: string;        // Text summary (for text content)
  image_url?: string;      // Image URL (for image content)
}`} />

          <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-xl p-4">
            <p className="text-sm text-gray-300">
              <strong className="text-cyan-400">Note:</strong> The <code className="text-cyan-300">urls</code> array
              contains source references used during verification. It may be empty if no external sources were referenced.
            </p>
          </div>
        </section>

        {/* Complete Example */}
        <section className="space-y-6">
          <div className="flex items-center gap-3">
            <FileCode className="text-cyan-400" size={28} />
            <h2 className="text-3xl font-bold text-white">Complete Example</h2>
          </div>

          <p className="text-gray-300">
            Here's a full working example that combines all the concepts:
          </p>

          <CodeBlock code={`import { useState, useEffect } from "react";
import { init, process, onReceive } from "satyamark-react";

function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Initialize connection on mount
  useEffect(() => {
    init({
      app_id: "my-app",
      user_id: \`user_\${Date.now()}\`
    });
  }, []);

  // Listen for results
  useEffect(() => {
    const unsubscribe = onReceive((data) => {
      setResult(data);
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const handleVerify = async () => {
    if (!text.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      await process(text, "", \`content_\${Date.now()}\`);
    } catch (error) {
      console.error("Verification failed:", error);
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">
        Content Verification
      </h1>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter text to verify..."
        className="w-full p-3 border rounded mb-4"
        rows={5}
      />

      <button
        onClick={handleVerify}
        disabled={loading || !text.trim()}
        className="bg-blue-500 text-white px-6 py-2 rounded"
      >
        {loading ? "Verifying..." : "Verify Content"}
      </button>

      {result && (
        <div className="mt-6 p-4 border rounded">
          <h2 className="font-bold text-lg mb-2">
            Result: {result.mark}
          </h2>
          <p className="text-gray-600 mb-2">
            Confidence: {result.confidence}%
          </p>
          <p className="text-sm">{result.reason}</p>
        </div>
      )}
    </div>
  );
}

export default App;`} />
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
                <li>• Initialize the connection once in your root App component</li>
                <li>• Use unique, stable IDs for content (e.g., database IDs)</li>
                <li>• Handle errors gracefully with try-catch blocks</li>
                <li>• Unsubscribe from listeners when components unmount</li>
                <li>• Show loading states while verification is in progress</li>
              </ul>
            </div>

            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-5">
              <h3 className="text-red-400 font-semibold mb-2">✗ Don't</h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>• Don't call init() multiple times or in multiple components</li>
                <li>• Don't use random IDs - they must be consistent for the same content</li>
                <li>• Don't submit empty strings or very short text (minimum 3 characters)</li>
                <li>• Don't forget to handle the case when WebSocket is disconnected</li>
                <li>• Don't block the UI while waiting for results</li>
              </ul>
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
