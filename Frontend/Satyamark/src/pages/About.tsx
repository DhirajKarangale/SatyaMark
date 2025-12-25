import { memo } from "react";
import { type Variants } from "framer-motion";
import { motion } from "framer-motion";
import { MARK_META } from "../utils/MARK_META";
import GradientText from "../reactbits/GradientText/GradientText";

const fadeUp: Variants = {
    hidden: { opacity: 0, y: 14 },
    visible: (i: number) => ({
        opacity: 1,
        y: 0,
        transition: { delay: 0.08 * i, duration: 0.4, ease: "easeOut" }
    })
};

function About() {
    return (
        <div className="min-h-screen w-full bg-transparent px-4 md:px-8 py-10">
            <motion.div
                initial="hidden"
                animate="visible"
                className="
          max-w-5xl mx-auto
          flex flex-col gap-12
          text-gray-300
        "
            >
                {/* HERO */}
                <motion.section custom={0} variants={fadeUp}>
                    <GradientText
                        colors={["#40ffaa", "#4079ff", "#40ffaa"]}
                        animationSpeed={6}
                        showBorder={false}
                        className="text-4xl md:text-5xl font-semibold"
                    >
                        SatyaMark
                    </GradientText>

                    <p className="mt-4 text-lg leading-relaxed text-gray-300 max-w-3xl">
                        SatyaMark is a centralized, AI-powered verification service designed
                        to help people and platforms distinguish truth from misinformation
                        in real time — across text, images, links, and media.
                    </p>
                </motion.section>

                {/* SDK */}
                <motion.section custom={7} variants={fadeUp} className="space-y-4">
                    <h2 className="text-white text-xl font-semibold">
                        React SDK
                    </h2>

                    <div
                        className="space-y-4 max-w-3xl"
                    >
                        <p className="leading-relaxed text-gray-300">
                            Official React SDK to embed verification marks, process content,
                            and receive real-time trust signals with minimal setup.
                        </p>

                        <div className="flex flex-wrap items-center gap-4">
                            <a
                                href="https://www.npmjs.com/package/satyamark-react"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="
                    text-cyan-400 hover:text-cyan-300
                    underline underline-offset-4
                "
                            >
                                View on npm →
                            </a>

                            <div className="flex gap-2">
                                <img
                                    src="https://img.shields.io/npm/v/satyamark-react?color=22c55e&label=version"
                                    alt="npm version"
                                />
                                <img
                                    src="https://img.shields.io/npm/dm/satyamark-react?color=38bdf8&label=downloads"
                                    alt="npm downloads"
                                />
                                <img
                                    src="https://img.shields.io/npm/l/satyamark-react?color=818cf8"
                                    alt="npm license"
                                />
                            </div>
                        </div>
                    </div>
                </motion.section>

                {/* PROBLEM */}
                <motion.section custom={1} variants={fadeUp} className="space-y-3">
                    <h2 className="text-white text-xl font-semibold">
                        The Problem We’re Solving
                    </h2>

                    <p className="leading-relaxed">
                        Misinformation spreads faster than facts across social platforms,
                        leading to confusion, mistrust, and real-world harm. Existing
                        fact-checking systems are slow, fragmented, and tightly coupled to
                        individual platforms — leaving users unsure what to trust.
                    </p>
                </motion.section>

                {/* WHY UNSOLVED */}
                <motion.section custom={2} variants={fadeUp} className="space-y-3">
                    <h2 className="text-white text-xl font-semibold">
                        Why This Remains Unsolved
                    </h2>

                    <ul className="list-disc pl-5 space-y-1">
                        <li>No unified, cross-platform verification layer</li>
                        <li>Limited detection of AI-generated or manipulated media</li>
                        <li>Lack of transparent, evidence-backed verdicts</li>
                    </ul>
                </motion.section>

                {/* SOLUTION */}
                <motion.section custom={3} variants={fadeUp} className="space-y-3">
                    <h2 className="text-white text-xl font-semibold">
                        Our Solution
                    </h2>

                    <p className="leading-relaxed">
                        SatyaMark provides a universal “mark of truth” for digital content.
                        Platforms integrate a lightweight SDK or API that displays trust
                        indicators next to posts. Users can inspect detailed verification
                        results, confidence scores, and sources — or request rechecks.
                    </p>
                </motion.section>

                {/* AI FLOW */}
                <motion.section custom={4} variants={fadeUp} className="space-y-3">
                    <h2 className="text-white text-xl font-semibold">
                        How the AI Works
                    </h2>

                    <ul className="list-disc pl-5 space-y-1">
                        <li>Ingests multi-modal content (text, images)</li>
                        <li>Extracts factual claims using NLP and vision models</li>
                        <li>
                            Cross-verifies claims using trusted sources, RAG, and vector search
                            (FAISS / Milvus)
                        </li>
                        <li>Detects AI-generated or synthetic media</li>
                        <li>
                            Assigns verdicts such as Correct, Incorrect, AI-Generated, Pending,
                            or Unverifiable — with confidence scores
                        </li>
                        <li>Continuously improves via user feedback and rechecks</li>
                    </ul>
                </motion.section>

                <motion.section className="space-y-4">
                    <h2 className="text-white text-xl font-semibold">
                        Verification Marks
                    </h2>

                    <p className="text-gray-400 max-w-3xl">
                        SatyaMark assigns clear, visual trust indicators to content so users
                        can instantly understand verification status.
                    </p>

                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 max-w-3xl">
                        {Object.values(MARK_META).map((mark, i) => (
                            <motion.div
                                key={mark.label}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.05 * i }}
                                className="flex flex-col gap-2
                                bg-white/5 border border-white/15 backdrop-blur-sm
                                rounded-xl px-4 py-3"
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
                </motion.section>

                {/* CURRENT STATUS & ROADMAP */}
                <motion.section custom={5} variants={fadeUp} className="space-y-3">
                    <h2 className="text-white text-xl font-semibold">
                        Current Capabilities & Roadmap
                    </h2>

                    <p className="leading-relaxed text-gray-400">
                        SatyaMark currently focuses on verification of text and images.
                        Text-based verification is the most mature and reliable, while
                        image verification is in an early stage and may have lower accuracy.
                    </p>

                    <p className="leading-relaxed text-gray-400">
                        We are continuously improving both text and image analysis pipelines,
                        including better claim extraction, reasoning quality, and forensic
                        detection. Over time, SatyaMark will introduce hybrid verification
                        techniques that combine multiple signals for higher confidence results.
                    </p>

                    <p className="leading-relaxed text-gray-400">
                        Support for video and audio verification is planned for future releases
                        as the platform evolves.
                    </p>
                </motion.section>

                {/* PRIVACY */}
                <motion.section custom={5} variants={fadeUp} className="space-y-3">
                    <h2 className="text-white text-xl font-semibold">
                        Privacy & Data Handling
                    </h2>

                    <p className="leading-relaxed">
                        SatyaMark does <span className="text-white font-medium">not</span>{" "}
                        use submitted content for advertising, profiling, or resale.
                    </p>

                    <p className="leading-relaxed text-gray-400">
                        For transparency and user reference, SatyaMark may store a short
                        AI-generated summary of submitted text rather than the full original
                        content. Images may be temporarily retained only to display verification
                        results on the SatyaMark platform.
                    </p>

                    <p className="leading-relaxed text-gray-400">
                        Verification is performed using a combination of self-hosted systems
                        and third-party Large Language Models (LLMs) accessed via Hugging Face.
                        These models process content solely to generate verification results.
                        Data handling by third-party providers is subject to their respective
                        privacy policies.
                    </p>
                </motion.section>

                {/* MODELS */}
                <motion.section custom={6} variants={fadeUp} className="space-y-3">
                    <h2 className="text-white text-xl font-semibold">
                        AI Models Used
                    </h2>

                    <p className="text-gray-400">
                        Depending on task and availability, SatyaMark may use models such as:
                    </p>

                    <ul className="list-disc pl-5 space-y-1 text-gray-300">
                        <li>LLaMA 3 (Meta)</li>
                        <li>Mistral 7B</li>
                        <li>DeepSeek R1 & V3</li>
                        <li>Hermes 3</li>
                        <li>Qwen 2.5</li>
                    </ul>
                </motion.section>

                {/* GTM */}
                <motion.section custom={7} variants={fadeUp} className="space-y-3">
                    <h2 className="text-white text-xl font-semibold">
                        Go-To-Market Strategy
                    </h2>

                    <ul className="list-disc pl-5 space-y-1">
                        <li>Pilot SDK with niche publishers and fact-checking NGOs</li>
                        <li>Partnerships with messaging apps and CMS platforms</li>
                        <li>Developer-first documentation and sample integrations</li>
                    </ul>
                </motion.section>

                {/* REVENUE */}
                <motion.section custom={8} variants={fadeUp} className="space-y-3">
                    <h2 className="text-white text-xl font-semibold">
                        Revenue Model
                    </h2>

                    <ul className="list-disc pl-5 space-y-1">
                        <li>Tiered API / SDK subscriptions</li>
                        <li>Advanced AI features for enterprise platforms</li>
                        <li>Analytics dashboards for moderation teams</li>
                    </ul>
                </motion.section>

                {/* CONTACT */}
                <motion.section
                    custom={9}
                    variants={fadeUp}
                    className="pt-6 border-t border-white/10 space-y-3"
                >
                    <h2 className="text-white text-xl font-semibold">Contact</h2>

                    <p>
                        Questions, feedback, or collaboration inquiries:
                    </p>

                    <a
                        href="mailto:dhirajkarangale02@gmail.com"
                        className="text-cyan-400 hover:text-cyan-300 underline w-fit"
                    >
                        dhirajkarangale02@gmail.com
                    </a>

                    <div className="flex gap-6 pt-2">
                        <a
                            href="https://dhirajkarangale.netlify.app/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:text-white transition"
                        >
                            Portfolio
                        </a>

                        <a
                            href="https://www.linkedin.com/in/dhiraj-karangale-464ab91bb/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:text-white transition"
                        >
                            LinkedIn
                        </a>
                    </div>
                </motion.section>
            </motion.div>
        </div>
    );
}

export default memo(About);
