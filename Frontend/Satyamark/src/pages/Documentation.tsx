import { memo } from "react";
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

function Doccumentation() {
    const url_git_main = import.meta.env.VITE_URL_GIT_MAIN;
    const url_git_demo = import.meta.env.VITE_URL_GIT_DEMO;
    const url_live_demo = import.meta.env.VITE_URL_LIVE_DEMO;
    const url_npm_library = import.meta.env.VITE_URL_NPM_LIBRARY;

    return (
        <div className="w-full bg-transparent px-4 md:px-8 py-10">
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
                        Doccumentation
                    </GradientText>

                    <p className="mt-4 text-lg leading-relaxed max-w-3xl">
                        This page explains how to integrate SatyaMark into a React application
                        and use it effectively — following the same pattern used in the demo
                        social media app.
                    </p>
                </motion.section>

                {/* OPEN SOURCE */}
                <motion.section custom={1} variants={fadeUp} className="space-y-3">
                    <h2 className="text-white text-xl font-semibold">
                        Open Source Project
                    </h2>

                    <p className="leading-relaxed">
                        SatyaMark is a fully open-source verification infrastructure designed
                        to surface transparent trust signals, not absolute truth.
                    </p>

                    <ul className="list-disc pl-5 space-y-1 text-gray-400">
                        <li>
                            Main Project Repository:{" "}
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
                            React SDK (npm):{" "}
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
                            Demo App Repository:{" "}
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
                                demo.vercel.app
                            </a>
                        </li>
                    </ul>
                </motion.section>

                {/* INSTALLATION */}
                <motion.section custom={2} variants={fadeUp} className="space-y-3">
                    <h2 className="text-white text-xl font-semibold">
                        Installation
                    </h2>

                    <pre className="bg-white/5 border border-white/15 rounded-xl p-4 text-sm overflow-x-auto">
                        <code>npm install satyamark-react</code>
                    </pre>
                </motion.section>

                {/* HOW TO USE */}
                <motion.section custom={3} variants={fadeUp} className="space-y-4">
                    <h2 className="text-white text-xl font-semibold">
                        How to Use SatyaMark Effectively
                    </h2>

                    <p className="text-gray-400 max-w-3xl">
                        The recommended way to integrate SatyaMark is to follow the same
                        pattern used in the demo application. Please go through the demo
                        app code on GitHub to understand the complete flow in a real UI.
                    </p>

                    <ol className="list-decimal pl-5 space-y-2">
                        <li>Initialize SatyaMark once when the app loads</li>
                        <li>Render your content normally (posts, cards, media)</li>
                        <li>Process the DOM element containing the content</li>
                        <li>Register a status container for live updates</li>
                        <li>Let SatyaMark update verification marks automatically</li>
                    </ol>
                </motion.section>

                {/* INIT */}
                <motion.section custom={4} variants={fadeUp} className="space-y-3">
                    <h2 className="text-white text-xl font-semibold">
                        1. Initialize the Connection
                    </h2>

                    <pre className="bg-white/5 border border-white/15 rounded-xl p-4 text-sm overflow-x-auto">
                        <code>{`import { useEffect } from "react";
import { init, onConnected } from "satyamark-react";

useEffect(() => {
  init({
    app_id: "YOUR_APP_ID",
    user_id: "UNIQUE_USER_ID",
  });
}, []);

onConnected((data) => {
  console.log("Connected:", data);
});`}</code>
                    </pre>
                </motion.section>

                {/* PROCESS */}
                <motion.section custom={5} variants={fadeUp} className="space-y-3">
                    <h2 className="text-white text-xl font-semibold">
                        2. Process Rendered Content
                    </h2>

                    <p className="text-gray-400">
                        SatyaMark extracts visible text and images from rendered UI —
                        exactly as users see them.
                    </p>

                    <pre className="bg-white/5 border border-white/15 rounded-xl p-4 text-sm overflow-x-auto">
                        <code>{`process(ref.current, "POST_ID")
  .then(setJobId)
  .catch(console.error);`}</code>
                    </pre>
                </motion.section>

                {/* STATUS */}
                <motion.section custom={6} variants={fadeUp} className="space-y-3">
                    <h2 className="text-white text-xl font-semibold">
                        3. Display Verification Status
                    </h2>

                    <pre className="bg-white/5 border border-white/15 rounded-xl p-4 text-sm overflow-x-auto">
                        <code>{`<div data-satyamark-status-container />`}</code>
                    </pre>

                    <pre className="bg-white/5 border border-white/15 rounded-xl p-4 text-sm overflow-x-auto">
                        <code>{`registerStatus(jobId, ref.current);`}</code>
                    </pre>
                </motion.section>

                {/* MARKS */}
                <motion.section custom={7} variants={fadeUp} className="space-y-4">
                    <h2 className="text-white text-xl font-semibold">
                        Verification Marks
                    </h2>

                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                        {Object.values(MARK_META).map((mark, i) => (
                            <motion.div
                                key={mark.label}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.05 * i }}
                                className="
                  bg-white/5 border border-white/15 backdrop-blur-sm
                  rounded-xl px-4 py-3 flex flex-col gap-2
                "
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

                {/* CONTRIBUTION */}
                <motion.section
                    custom={8}
                    variants={fadeUp}
                    className="pt-6 border-t border-white/10 space-y-3"
                >
                    <h2 className="text-white text-xl font-semibold">
                        Help Improve This Documentation
                    </h2>

                    <p className="text-gray-400">
                        This documentation is open for improvement. If you think something
                        can be clearer, better structured, or more helpful for developers,
                        feel free to raise a Pull Request.
                    </p>

                    <p className="text-gray-400">
                        If the change aligns with SatyaMark’s principles, it will be reviewed
                        and approved.
                    </p>
                </motion.section>
            </motion.div>
        </div>
    );
}

export default memo(Doccumentation);
