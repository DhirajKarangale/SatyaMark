import { memo, useState, useEffect } from "react";
import Alert from "./Alert";
import { motion } from "framer-motion";
import { type Variants } from "framer-motion";
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
    const hasPendingJobs = jobStore.hasJobs();
    const [showAlert, setShowAlert] = useState<boolean>(false);
    const [data, setData] = useState<ResultData | null>(null);
    const [receivedData, setReceivedData] = useState<ResultData | null>(null);

    const cardVariants: Variants = {
        hidden: { opacity: 0, scale: 0.95 },
        visible: { opacity: 1, scale: 1, transition: { duration: 0.35, ease: "easeOut" } }
    };

    const contentVariants = {
        hidden: { opacity: 0, y: 10 },
        visible: (i: number) => ({
            opacity: 1,
            y: 0,
            transition: { delay: 0.1 + i * 0.05, duration: 0.35 }
        })
    };

    onReceive((receivedData) => {
        if (!receivedData?.jobId) return;

        if (data != null) {
            setShowAlert(true);
            setReceivedData(receivedData);
        }
        else {
            setData(receivedData);
        }
    });

    useEffect(() => {
        const unsubscribe = onReceive((received) => {
            if (!received?.jobId) return;

            jobStore.remove(received.jobId);

            if (data) {
                setShowAlert(true);
                setReceivedData(received);
            } else {
                setData(received);
            }
        });

        return unsubscribe;
    }, [data]);

    useEffect(() => {
        return jobStore.subscribe(() => forceUpdate(v => v + 1));
    }, []);

    if (!data) {
        if (jobStore.hasJobs()) {
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
                whileHover={{ scale: 1, boxShadow: "0 0 20px rgba(64,255,170,0.25)" }}
                className="w-full h-full border border-white/20 bg-transparent
                backdrop-blur-sm rounded-xl p-4 flex items-center justify-center"
            >
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4 }}
                >
                    <GradientText
                        colors={["#40ffaa", "#4079ff", "#40ffaa", "#4079ff", "#40ffaa"]}
                        animationSpeed={6}
                        showBorder={false}
                        className="text-3xl font-semibold"
                    >
                        Welcome to Satyamark
                    </GradientText>
                </motion.div>
            </motion.div>
        );
    }

    return (
        <>
            <motion.div
                variants={cardVariants}
                initial="hidden"
                animate="visible"
                whileHover={{
                    scale: 1,
                    boxShadow: "0 0 25px rgba(0,200,255,0.25)"
                }}
                className="relative w-full h-full bg-white/5 border border-white/20 backdrop-blur-sm 
                flex flex-col gap-4 overflow-y-auto custom-scroll rounded-xl p-4"
            >
                {/* TOP ROW */}
                <motion.div
                    custom={0}
                    variants={contentVariants}
                    initial="hidden"
                    animate="visible"
                    className="flex justify-between items-center w-full"
                >
                    <div className="text-white text-lg font-semibold">
                        ID: {data.dataId}
                    </div>

                    <div className="flex items-center gap-4">
                        <span className="text-cyan-400 font-medium">
                            Mark: {data.mark}
                        </span>
                        <span className="text-green-400 font-medium">
                            Confidence: {data.confidence}
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
                    {data.reason}
                </motion.div>

                {/* URLS */}
                {data.urls && data.urls.length > 0 && (
                    <motion.div
                        custom={2}
                        variants={contentVariants}
                        initial="hidden"
                        animate="visible"
                        className="flex flex-col gap-2"
                    >
                        <div className="text-white font-semibold">Sources:</div>

                        <div className="flex flex-col gap-1">
                            {data.urls.map((url, index) => (
                                <motion.a
                                    key={index}
                                    href={url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    whileHover={{ x: 4 }}
                                    className="text-cyan-400 hover:text-cyan-300 underline break-all"
                                >
                                    {url}
                                </motion.a>
                            ))}
                        </div>
                    </motion.div>
                )}

                {data && hasPendingJobs && (
                    <div className="absolute bottom-4 right-4 flex items-center gap-2
                  bg-black/40 backdrop-blur-md px-3 py-2 rounded-lg
                  border border-white/20">
                        <div className="w-4 h-4 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
                        <span className="text-xs text-cyan-300">
                            Processing next…
                        </span>
                    </div>
                )}

            </motion.div>

            <Alert
                isOpen={showAlert}
                message="This will remove the current data from this page."
                onClose={() => setShowAlert(false)}
                onConfirm={() => setData(receivedData)}
            />
        </>
    );
}

export default memo(ResultCard);
