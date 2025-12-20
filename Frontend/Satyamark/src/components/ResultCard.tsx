import Alert from "./Alert";
import { jobStore } from "../store/jobStore";
import { resultBus } from "../store/resultBus";
import { memo, useState, useEffect } from "react";
import { motion, type Variants } from "framer-motion";
import { onReceive } from "../process/satyamark_connect";
import { process } from "../process/satyamark_process";
import { getDataId } from "../utils/GenerateIds";
import GradientText from "../reactbits/GradientText/GradientText";

type ResultData = {
    dataId: string | number;
    mark: string;
    confidence: number | string;
    reason: string;
    urls?: string[] | null;

    type?: "text" | "image";
    summary?: string;
    image_url?: string;
};

function ResultCard() {
    const [, forceUpdate] = useState(0);
    const urlBase = import.meta.env.VITE_URL_BASE;

    const [currentData, setCurrentData] = useState<ResultData | null>(null);
    const [queue, setQueue] = useState<ResultData[]>([]);
    const [showAlert, setShowAlert] = useState(false);
    const STORAGE_KEY = "satyamark_result_state";

    const [recheckMsg, setRecheckMsg] = useState("");
    const [recheckLoading, setRecheckLoading] = useState(false);
    const [showRecheckPopup, setShowRecheckPopup] = useState(false);

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

    function LazyImage({ src }: { src: string }) {
        const [loaded, setLoaded] = useState(false);

        return (
            <div className="relative w-full flex justify-center rounded-xl">

                {!loaded && (
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
                    </div>
                )}

                <img
                    src={src}
                    loading="lazy"
                    onLoad={() => setLoaded(true)}
                    className={`
                        max-h-[200px]
                        w-auto
                        max-w-full
                        object-contain
                        transition-opacity duration-300
                        ${loaded ? "opacity-100" : "opacity-0"}
                    `}
                />
            </div>
        );
    }

    function Section({
        title,
        children
    }: {
        title: string;
        children: React.ReactNode;
    }) {
        return (
            <div className="flex flex-col gap-2">
                <div className="text-xs uppercase tracking-wider text-cyan-400 font-semibold">
                    {title}
                </div>
                <div className="bg-white/5 border border-white/10
                    rounded-lg p-3 text-gray-200 leading-relaxed">
                    {children}
                </div>
            </div>
        );
    }

    const handleRecheckConfirm = async () => {
        if (!currentData) return;

        try {
            setRecheckLoading(true);
            setRecheckMsg("");

            const endpoint = currentData.type === "image" ? "/image/remove" : "/text/remove";
            const api = `${urlBase}${endpoint}`

            const res = await fetch(api, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id: currentData.dataId })
            });

            const data = await res.json();

            if (!res.ok || !data.success) {
                throw new Error(data.message || "Recheck failed");
            }

            const jobId = await process(
                currentData.summary ?? "",
                currentData.image_url ?? "",
                getDataId()
            );

            if (jobId) jobStore.add(jobId);

            setRecheckMsg("Recheck request submitted successfully");

            setTimeout(() => {
                setShowRecheckPopup(false);

                setQueue((q) => {
                    if (q.length === 0) {
                        setCurrentData(null);
                        return q;
                    }

                    const [next, ...rest] = q;
                    setCurrentData(next);
                    return rest;
                });

                setRecheckLoading(false);
            }, 800);

        } catch (err) {
            setRecheckMsg(
                err instanceof Error ? err.message : "Something went wrong"
            );
            setRecheckLoading(false);
        }
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

    const showLoader = !currentData && queue.length === 0 && jobStore.hasJobs();

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
                className="w-full h-full bg-white/5 border border-white/20
                backdrop-blur-sm flex flex-col gap-1 rounded-xl p-4"
            >
                <div className="relative w-full h-full flex flex-col gap-4 overflow-y-auto custom-scroll">
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

                    {currentData.type === "text" && currentData.summary && (
                        <motion.div
                            custom={1}
                            variants={contentVariants}
                            initial="hidden"
                            animate="visible"
                        >
                            <Section title="Input">
                                <div className="whitespace-pre-wrap">
                                    {currentData.summary}
                                </div>
                            </Section>
                        </motion.div>
                    )}

                    {currentData.type === "image" && currentData.image_url && (
                        <motion.div
                            custom={1}
                            variants={contentVariants}
                            initial="hidden"
                            animate="visible"
                        >
                            <Section title="Image">
                                <LazyImage src={currentData.image_url} />
                            </Section>
                        </motion.div>
                    )}

                    <motion.div
                        custom={2}
                        variants={contentVariants}
                        initial="hidden"
                        animate="visible"
                    >
                        <Section title="Reason">
                            <div className="whitespace-pre-wrap">
                                {currentData.reason}
                            </div>
                        </Section>
                    </motion.div>

                    {currentData.urls?.length ? (
                        <motion.div
                            custom={3}
                            variants={contentVariants}
                            initial="hidden"
                            animate="visible"
                        >
                            <Section title="Sources">
                                <div className="flex flex-col gap-2">
                                    {currentData.urls.map((url, i) => (
                                        <a
                                            key={i}
                                            href={url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-cyan-400 underline break-all hover:text-cyan-300"
                                        >
                                            {url}
                                        </a>
                                    ))}
                                </div>
                            </Section>
                        </motion.div>
                    ) : null}
                </div>


                <div className="w-full h-11">
                    <button
                        onClick={() => setShowRecheckPopup(true)}
                        className="absolute bottom-4 left-4
                        bg-orange-500/20 border border-orange-400
                        text-orange-300 text-xs px-3 py-2 rounded-lg
                        hover:bg-orange-500/30 transition"
                    >
                        Recheck
                    </button>

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
                </div>

            </motion.div>

            <Alert
                isOpen={showAlert}
                message="New result is ready. Load it now?"
                onClose={() => setShowAlert(false)}
                onConfirm={loadNext}
            />

            <Alert
                isOpen={showRecheckPopup}
                message={recheckMsg || "Are you sure you want to recheck this result?"}
                onClose={() => setShowRecheckPopup(false)}
                onConfirm={handleRecheckConfirm}
                disableClose={recheckLoading}
                disableConfirm={recheckLoading}
            />
        </>
    );
}

export default memo(ResultCard);