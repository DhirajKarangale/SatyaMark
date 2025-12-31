import { memo } from "react";
import { motion, type Variants } from "framer-motion";
import { Link } from "react-router-dom";
import { MARK_META } from "../utils/MARK_META";
import { routeChat, routeDoccu } from "../utils/Routes";
import { CheckCircle2, XCircle, AlertCircle, Sparkles, Github, ExternalLink, Package } from "lucide-react";

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.1 * i, duration: 0.5, ease: "easeOut" }
  })
};

function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-gray-100">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-linear-to-b from-slate-900 via-slate-950 to-slate-950">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-cyan-500/10 via-transparent to-transparent" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,_var(--tw-gradient-stops))] from-blue-500/10 via-transparent to-transparent" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
          <motion.div
            initial="hidden"
            animate="visible"
            className="text-center space-y-8"
          >
            <motion.div custom={0} variants={fadeUp} className="space-y-4">
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight">
                <span className="bg-linear-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
                  SatyaMark
                </span>
              </h1>
              <p className="text-xl sm:text-2xl text-gray-400 max-w-3xl mx-auto">
                AI-Powered Content Verification for the Modern Web
              </p>
            </motion.div>

            <motion.p
              custom={1}
              variants={fadeUp}
              className="text-lg text-gray-300 max-w-2xl mx-auto leading-relaxed"
            >
              A centralized verification platform that helps users and platforms
              distinguish truth from misinformation in real-time — across text,
              images, and media.
            </motion.p>

            <motion.div
              custom={2}
              variants={fadeUp}
              className="flex flex-wrap items-center justify-center gap-4 pt-4"
            >
              {/* <Link
                  to={routeChat}
                  className="inline-flex items-center gap-2 px-8 py-3 
                      bg-linear-to-r from-cyan-600 to-blue-600 
                      hover:from-cyan-500 hover:to-blue-500
                      text-white font-semibold rounded-lg 
                      shadow-lg shadow-cyan-500/25 
                      transition-all duration-200 hover:scale-105"
              >
                  Try Live Demo
                  <ExternalLink size={18} />
              </Link> */}

              <a
                href="https://satyamark-demo-socialmedia.vercel.app/"
                target="_blank"
                className="inline-flex items-center gap-2 px-8 py-3 
                bg-linear-to-r from-cyan-600 to-blue-600 
                hover:from-cyan-500 hover:to-blue-500
                text-white font-semibold rounded-lg 
                shadow-lg shadow-cyan-500/25 
                transition-all duration-200 hover:scale-105"
              >
                Try Live Demo
                <ExternalLink size={18} />
              </a>

              <a
                href="https://github.com/DhirajKarangale/SatyaMark"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-8 py-3 
                                    bg-white/5 hover:bg-white/10 
                                    border border-white/20 
                                    text-white font-semibold rounded-lg 
                                    transition-all duration-200 hover:scale-105"
              >
                <Github size={18} />
                View on GitHub
              </a>

              <a
                href="https://www.npmjs.com/package/satyamark-react"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-8 py-3 
                                    bg-white/5 hover:bg-white/10 
                                    border border-white/20 
                                    text-white font-semibold rounded-lg 
                                    transition-all duration-200 hover:scale-105"
              >
                <Package size={18} />
                NPM Package
              </a>
            </motion.div>

            {/* NPM Badges */}
            <motion.div
              custom={3}
              variants={fadeUp}
              className="flex flex-wrap items-center justify-center gap-3 pt-6"
            >
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

      {/* Problem Section */}
      <section className="py-20 bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            className="grid md:grid-cols-2 gap-12 items-center"
          >
            <motion.div custom={0} variants={fadeUp} className="space-y-6">
              <h2 className="text-3xl sm:text-4xl font-bold text-white">
                The Misinformation Problem
              </h2>
              <p className="text-lg text-gray-300 leading-relaxed">
                Misinformation spreads faster than facts across social platforms,
                leading to confusion, mistrust, and real-world harm. Existing
                fact-checking systems are slow, fragmented, and tightly coupled
                to individual platforms.
              </p>
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <XCircle className="text-red-400 mt-1 shrink-0" size={20} />
                  <p className="text-gray-400">No unified, cross-platform verification layer</p>
                </div>
                <div className="flex items-start gap-3">
                  <XCircle className="text-red-400 mt-1 shrink-0" size={20} />
                  <p className="text-gray-400">Limited detection of AI-generated media</p>
                </div>
                <div className="flex items-start gap-3">
                  <XCircle className="text-red-400 mt-1 shrink-0" size={20} />
                  <p className="text-gray-400">Lack of transparent, evidence-backed verdicts</p>
                </div>
              </div>
            </motion.div>

            <motion.div custom={1} variants={fadeUp} className="space-y-6">
              <h2 className="text-3xl sm:text-4xl font-bold text-white">
                Our Solution
              </h2>
              <p className="text-lg text-gray-300 leading-relaxed">
                SatyaMark provides a universal "mark of truth" for digital content.
                Platforms integrate a lightweight SDK that displays trust indicators
                next to posts. Users can inspect detailed verification results,
                confidence scores, and sources.
              </p>
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="text-green-400 mt-1 shrink-0" size={20} />
                  <p className="text-gray-400">Real-time verification of text and images</p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="text-green-400 mt-1 shrink-0" size={20} />
                  <p className="text-gray-400">Evidence-backed verdicts with confidence scores</p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="text-green-400 mt-1 shrink-0" size={20} />
                  <p className="text-gray-400">Easy integration with React SDK</p>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-linear-to-b from-slate-950 to-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            className="text-center space-y-12"
          >
            <motion.div custom={0} variants={fadeUp}>
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                How SatyaMark Works
              </h2>
              <p className="text-lg text-gray-400 max-w-2xl mx-auto">
                Our AI-powered system analyzes content through multiple layers of verification
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8">
              <motion.div
                custom={1}
                variants={fadeUp}
                className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-4
                                    hover:bg-white/10 transition-all duration-300"
              >
                <div className="w-12 h-12 rounded-xl bg-cyan-500/20 
                                    flex items-center justify-center text-cyan-400">
                  <Sparkles size={24} />
                </div>
                <h3 className="text-xl font-semibold text-white">Content Extraction</h3>
                <p className="text-gray-400 leading-relaxed">
                  Extracts factual claims using NLP and vision models from text and images
                </p>
              </motion.div>

              <motion.div
                custom={2}
                variants={fadeUp}
                className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-4
                                    hover:bg-white/10 transition-all duration-300"
              >
                <div className="w-12 h-12 rounded-xl bg-blue-500/20 
                                    flex items-center justify-center text-blue-400">
                  <CheckCircle2 size={24} />
                </div>
                <h3 className="text-xl font-semibold text-white">Cross-Verification</h3>
                <p className="text-gray-400 leading-relaxed">
                  Verifies claims using trusted sources, RAG, vector search, and AI detection
                </p>
              </motion.div>

              <motion.div
                custom={3}
                variants={fadeUp}
                className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-4
                                    hover:bg-white/10 transition-all duration-300"
              >
                <div className="w-12 h-12 rounded-xl bg-purple-500/20 
                                    flex items-center justify-center text-purple-400">
                  <AlertCircle size={24} />
                </div>
                <h3 className="text-xl font-semibold text-white">Verdict Assignment</h3>
                <p className="text-gray-400 leading-relaxed">
                  Assigns verification marks with confidence scores and detailed explanations
                </p>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Verification Marks */}
      <section className="py-20 bg-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            className="space-y-12"
          >
            <motion.div custom={0} variants={fadeUp} className="text-center">
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                Verification Marks
              </h2>
              <p className="text-lg text-gray-400 max-w-2xl mx-auto">
                Clear, visual trust indicators that are instantly understandable
              </p>
            </motion.div>

            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.values(MARK_META).map((mark, i) => (
                <motion.div
                  key={mark.label}
                  custom={i + 1}
                  variants={fadeUp}
                  className="bg-white/5 border border-white/10 rounded-xl p-5 
                                        hover:bg-white/10 hover:border-white/20 
                                        transition-all duration-300 space-y-3"
                >
                  <div className="flex items-center gap-3">
                    <img
                      src={mark.icon}
                      alt={mark.label}
                      className="w-8 h-8 object-contain"
                    />
                    <span className={`font-semibold text-lg ${mark.color}`}>
                      {mark.label}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 leading-relaxed">
                    {mark.description}
                  </p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            className="space-y-12"
          >
            <motion.div custom={0} variants={fadeUp} className="text-center">
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                Key Features
              </h2>
              <p className="text-lg text-gray-400 max-w-2xl mx-auto">
                Built for developers, trusted by users
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 gap-8">
              <motion.div
                custom={1}
                variants={fadeUp}
                className="bg-linear-to-br from-cyan-500/10 to-blue-500/10 
                                    border border-cyan-500/20 rounded-2xl p-8 space-y-4"
              >
                <h3 className="text-2xl font-bold text-white">React SDK</h3>
                <p className="text-gray-300 leading-relaxed">
                  Official React library for seamless integration. Display verification
                  marks with minimal setup and receive real-time updates via WebSocket.
                </p>
                <div className="flex gap-3 pt-2">
                  <a
                    href="https://www.npmjs.com/package/satyamark-react"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-cyan-400 hover:text-cyan-300 font-medium 
                                            inline-flex items-center gap-1"
                  >
                    View Package <ExternalLink size={16} />
                  </a>
                  <Link
                    to={routeDoccu}
                    className="text-blue-400 hover:text-blue-300 font-medium"
                  >
                    Documentation →
                  </Link>
                </div>
              </motion.div>

              <motion.div
                custom={2}
                variants={fadeUp}
                className="bg-linear-to-br from-purple-500/10 to-pink-500/10 
                                    border border-purple-500/20 rounded-2xl p-8 space-y-4"
              >
                <h3 className="text-2xl font-bold text-white">Privacy First</h3>
                <p className="text-gray-300 leading-relaxed">
                  No advertising, profiling, or data resale. Content is processed
                  ephemerally. Only short AI-generated summaries are stored for
                  transparency.
                </p>
              </motion.div>

              <motion.div
                custom={3}
                variants={fadeUp}
                className="bg-linear-to-br from-green-500/10 to-emerald-500/10 
                                    border border-green-500/20 rounded-2xl p-8 space-y-4"
              >
                <h3 className="text-2xl font-bold text-white">Open Source</h3>
                <p className="text-gray-300 leading-relaxed">
                  Fully open-source and transparent. Review the code, contribute
                  improvements, and help build trust infrastructure for the internet.
                </p>
                <a
                  href="https://github.com/DhirajKarangale/SatyaMark"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-green-400 hover:text-green-300 font-medium 
                                        inline-flex items-center gap-1"
                >
                  View on GitHub <ExternalLink size={16} />
                </a>
              </motion.div>

              <motion.div
                custom={4}
                variants={fadeUp}
                className="bg-linear-to-br from-orange-500/10 to-red-500/10 
                                    border border-orange-500/20 rounded-2xl p-8 space-y-4"
              >
                <h3 className="text-2xl font-bold text-white">Live Demo</h3>
                <p className="text-gray-300 leading-relaxed">
                  Experience SatyaMark in action with our social media demo.
                  See how verification marks appear in a real-world context.
                </p>
                <a
                  href="https://satyamark-demo-socialmedia.vercel.app/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-orange-400 hover:text-orange-300 font-medium 
                                        inline-flex items-center gap-1"
                >
                  Try Demo <ExternalLink size={16} />
                </a>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-linear-to-b from-slate-950 to-slate-900">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="space-y-8"
          >
            <motion.h2
              custom={0}
              variants={fadeUp}
              className="text-3xl sm:text-4xl font-bold text-white"
            >
              Ready to Build Trust?
            </motion.h2>

            <motion.p
              custom={1}
              variants={fadeUp}
              className="text-lg text-gray-300"
            >
              Start integrating SatyaMark into your platform today
            </motion.p>

            <motion.div
              custom={2}
              variants={fadeUp}
              className="flex flex-wrap items-center justify-center gap-4"
            >
              <Link
                to={routeDoccu}
                className="inline-flex items-center gap-2 px-8 py-3 
                                    bg-linear-to-r from-cyan-600 to-blue-600 
                                    hover:from-cyan-500 hover:to-blue-500
                                    text-white font-semibold rounded-lg 
                                    shadow-lg shadow-cyan-500/25 
                                    transition-all duration-200 hover:scale-105"
              >
                Get Started
                <ExternalLink size={18} />
              </Link>

              <a
                href="https://www.linkedin.com/in/dhiraj-karangale-464ab91bb/"
                target="_blank"
                className="inline-flex items-center gap-2 px-8 py-3 
                                    bg-white/5 hover:bg-white/10 
                                    border border-white/20 
                                    text-white font-semibold rounded-lg 
                                    transition-all duration-200 hover:scale-105"
              >
                Contact Us
              </a>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-950 border-t border-white/10 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="space-y-4">
              <h3 className="text-white font-semibold text-lg">SatyaMark</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                AI-powered content verification infrastructure for the modern web
              </p>
            </div>

            <div className="space-y-4">
              <h3 className="text-white font-semibold text-lg">Links</h3>
              <div className="flex flex-col gap-2">
                <Link to={routeChat} className="text-gray-400 hover:text-cyan-400 text-sm">
                  Live Demo
                </Link>
                <Link to={routeDoccu} className="text-gray-400 hover:text-cyan-400 text-sm">
                  Documentation
                </Link>
                <a
                  href="https://github.com/DhirajKarangale/SatyaMark"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-cyan-400 text-sm"
                >
                  GitHub
                </a>
                <a
                  href="https://www.npmjs.com/package/satyamark-react"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-cyan-400 text-sm"
                >
                  NPM Package
                </a>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-white font-semibold text-lg">Contact</h3>
              <div className="flex flex-col gap-2 text-sm">
                <a
                  href="mailto:dhirajkarangale02@gmail.com"
                  className="text-gray-400 hover:text-cyan-400"
                >
                  dhirajkarangale02@gmail.com
                </a>
                <a
                  href="https://dhirajkarangale.netlify.app/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-cyan-400"
                >
                  Portfolio
                </a>
                <a
                  href="https://www.linkedin.com/in/dhiraj-karangale-464ab91bb/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-cyan-400"
                >
                  LinkedIn
                </a>
              </div>
            </div>
          </div>

          <div className="mt-12 pt-8 border-t border-white/10 text-center text-sm text-gray-400">
            <p>&copy; {new Date().getFullYear()} SatyaMark. Open source trust infrastructure.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default memo(Home);
