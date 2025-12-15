import { memo, useState, useEffect } from "react";
import Alert from "./Alert";
import { motion, type Variants } from "framer-motion";
import { jobStore } from "../store/jobStore";
import { onReceive } from "../process/satyamark_connect";
import GradientText from "../reactbits/GradientText/GradientText";

type ResultData = {
    dataId: string | number;
    mark: string;
    confidence: number | string;
    reason: string;
    urls?: string[] | null;
};

function ResultCard() {
    const [, forceUpdate] = useState(0);

    const [currentData, setCurrentData] = useState<ResultData | null>(null);
    const [queue, setQueue] = useState<ResultData[]>([]);
    const [showAlert, setShowAlert] = useState(false);

    /* ---------------- animations ---------------- */

    const cardVariants: Variants = {
        hidden: { opacity: 0, scale: 0.95 },
        visible: {
            opacity: 1,
            scale: 1,
            transition: { duration: 0.35, ease: "easeOut" }
        }
    };

    const contentVariants = {
        hidden: { opacity: 0, y: 10 },
        visible: (i: number) => ({
            opacity: 1,
            y: 0,
            transition: { delay: 0.1 + i * 0.05, duration: 0.35 }
        })
    };

    /* ---------------- receive + queue ---------------- */

    useEffect(() => {
        const unsubscribe = onReceive((received) => {
            if (!received?.jobId) return;

            jobStore.remove(received.jobId);

            setQueue((q) => {
                if (!currentData) {
                    setCurrentData(received);
                    return q;
                }

                setShowAlert(true);
                return [...q, received];
            });
        });

        return unsubscribe;
    }, [currentData]);

    /* ---------------- job store rerender ---------------- */

    useEffect(() => {
        return jobStore.subscribe(() => forceUpdate(v => v + 1));
    }, []);

    /* ---------------- helpers ---------------- */

    const loadNext = () => {
        setQueue((q) => {
            if (q.length === 0) return q;
            setCurrentData(q[0]);
            return q.slice(1);
        });
        setShowAlert(false);
    };

    const showLoader =
        !currentData &&
        queue.length === 0 &&
        jobStore.hasJobs();

    /* ---------------- empty / loader ---------------- */

    if (!currentData) {
        if (showLoader) {
            const jobs = jobStore.list();

            return (
                <div className="w-full h-full flex flex-col items-center justify-center gap-4">
                    <div className="animate-spin w-12 h-12 rounded-full border-4 border-cyan-400 border-t-transparent" />
                    <div className="text-gray-300 text-center">
                        Processing your data<br />
                        <span className="text-cyan-400 text-sm">
                            Job ID: {jobs[jobs.length - 1]}
                        </span>
                    </div>
                </div>
            );
        }

        return (
            <motion.div
                variants={cardVariants}
                initial="hidden"
                animate="visible"
                className="w-full h-full border border-white/20 bg-transparent
                backdrop-blur-sm rounded-xl p-4 flex items-center justify-center"
            >
                <GradientText
                    colors={["#40ffaa", "#4079ff", "#40ffaa"]}
                    animationSpeed={6}
                    showBorder={false}
                    className="text-3xl font-semibold"
                >
                    Welcome to Satyamark
                </GradientText>
            </motion.div>
        );
    }

    /* ---------------- main card ---------------- */

    return (
        <>
            <motion.div
                variants={cardVariants}
                initial="hidden"
                animate="visible"
                className="relative w-full h-full bg-white/5 border border-white/20
                backdrop-blur-sm flex flex-col gap-4 overflow-y-auto
                custom-scroll rounded-xl p-4"
            >
                {/* TOP */}
                <motion.div
                    custom={0}
                    variants={contentVariants}
                    initial="hidden"
                    animate="visible"
                    className="flex justify-between items-center"
                >
                    <div className="text-white text-lg font-semibold">
                        ID: {currentData.dataId}
                    </div>

                    <div className="flex items-center gap-4">
                        <span className="text-cyan-400 font-medium">
                            Mark: {currentData.mark}
                        </span>
                        <span className="text-green-400 font-medium">
                            Confidence: {currentData.confidence}
                        </span>
                    </div>
                </motion.div>

                {/* REASON */}
                <motion.div
                    custom={1}
                    variants={contentVariants}
                    initial="hidden"
                    animate="visible"
                    className="text-gray-300 whitespace-pre-wrap leading-relaxed"
                >
                    {currentData.reason}
                </motion.div>

                {/* URLS */}
                {currentData.urls?.length ? (
                    <motion.div
                        custom={2}
                        variants={contentVariants}
                        initial="hidden"
                        animate="visible"
                        className="flex flex-col gap-2"
                    >
                        <div className="text-white font-semibold">Sources</div>
                        {currentData.urls.map((url, i) => (
                            <a
                                key={i}
                                href={url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-cyan-400 underline break-all"
                            >
                                {url}
                            </a>
                        ))}
                    </motion.div>
                ) : null}

                {/* LOAD NEXT BUTTON */}
                {queue.length > 0 && (
                    <button
                        onClick={loadNext}
                        className="absolute bottom-4 right-4
                        bg-cyan-500/20 border border-cyan-400
                        text-cyan-300 text-xs px-3 py-2 rounded-lg
                        hover:bg-cyan-500/30 transition"
                    >
                        Load next ({queue.length})
                    </button>
                )}

                {/* PROCESSING INDICATOR */}
                {queue.length === 0 && jobStore.hasJobs() && (
                    <div className="absolute bottom-4 right-4 flex items-center gap-2
                    bg-black/40 backdrop-blur-md px-3 py-2 rounded-lg
                    border border-white/20">
                        <div className="w-4 h-4 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
                        <span className="text-xs text-cyan-300">
                            Processing…
                        </span>
                    </div>
                )}
            </motion.div>

            {/* ALERT */}
            <Alert
                isOpen={showAlert}
                message="New result is ready. Load it now?"
                onClose={() => setShowAlert(false)}
                onConfirm={loadNext}
            />
        </>
    );
}

export default memo(ResultCard);
