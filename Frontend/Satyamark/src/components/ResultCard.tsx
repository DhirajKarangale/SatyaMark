import Alert from "./Alert";
import { jobStore } from "../store/jobStore";
import { resultBus } from "../store/resultBus";
import { memo, useState, useEffect } from "react";
import { motion, type Variants } from "framer-motion";
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
    const STORAGE_KEY = "satyamark_result_state";

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

    const isSameResult = (a: ResultData, b: ResultData) => {
        if (a.dataId !== b.dataId) return false;
        if (a.mark !== b.mark) return false;
        if (a.confidence !== b.confidence) return false;
        if (a.reason !== b.reason) return false;

        if (a.urls === null && b.urls === null) return true;
        if (!a.urls || !b.urls) return false;
        if (a.urls.length !== b.urls.length) return false;

        for (let i = 0; i < a.urls.length; i++) {
            if (a.urls[i] !== b.urls[i]) return false;
        }

        return true;
    };

    useEffect(() => {
        const saved = sessionStorage.getItem(STORAGE_KEY);
        if (!saved) return;

        try {
            const { currentData, queue } = JSON.parse(saved);
            setCurrentData(currentData ?? null);
            setQueue(queue ?? []);
        } catch { }
    }, []);

    useEffect(() => {
        sessionStorage.setItem(
            STORAGE_KEY,
            JSON.stringify({ currentData, queue })
        );
    }, [currentData, queue]);

    useEffect(() => {
        const unsubscribe = onReceive((received) => {
            if (!received?.jobId) return;

            jobStore.remove(received.jobId);

            setQueue((q) => {
                if (!currentData) {
                    setCurrentData(received);
                    return q;
                }

                const alreadyExists =
                    isSameResult(currentData, received) ||
                    q.some(item => isSameResult(item, received));

                if (alreadyExists) return q;

                setShowAlert(true);
                return [...q, received];
            });
        });

        return unsubscribe;
    }, [currentData]);

    useEffect(() => {
        const unsubscribe = resultBus.subscribe((data) => {
            const parsedData = {
                ...data,
                dataId: data.id,
            };
            delete parsedData.id;

            setQueue((q) => {
                if (!currentData) {
                    setCurrentData(parsedData);
                    return q;
                }

                const alreadyExists =
                    isSameResult(currentData, parsedData) ||
                    q.some(item => isSameResult(item, parsedData));

                if (alreadyExists) return q;

                setShowAlert(true);

                return [parsedData, ...q];
            });
        });

        return unsubscribe;
    }, [currentData]);

    useEffect(() => {
        return jobStore.subscribe(() => forceUpdate(v => v + 1));
    }, []);

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

                <motion.div
                    custom={1}
                    variants={contentVariants}
                    initial="hidden"
                    animate="visible"
                    className="text-gray-300 whitespace-pre-wrap leading-relaxed"
                >
                    {currentData.reason}
                </motion.div>

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