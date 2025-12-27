import Alert from "./Alert";
import { jobStore } from "../store/jobStore";
import { resultBus } from "../store/resultBus";
import { memo, useState, useEffect } from "react";
import { motion, type Variants } from "framer-motion";
import { onReceive } from "../process/satyamark_connect";
import { process } from "../process/satyamark_process";
import { getDataId } from "../utils/GenerateIds";
import { isSocketConnected, onConnectionChange } from "../process/satyamark_connect";
import { MARK_META } from "../utils/MARK_META";
import { ExternalLink, RotateCcw, Loader2, ChevronRight } from "lucide-react";

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
  const [connected, setConnected] = useState(isSocketConnected());
  const STORAGE_KEY = "satyamark_result_state";

  const [recheckMsg, setRecheckMsg] = useState("");
  const [recheckLoading, setRecheckLoading] = useState(false);
  const [showRecheckPopup, setShowRecheckPopup] = useState(false);

  const RECHECK_GENERIC_ERROR = "We can't process the recheck right now. Please try again later.";

  const cardVariants: Variants = {
    hidden: { opacity: 0, scale: 0.98 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: { duration: 0.4, ease: "easeOut" }
    }
  };

  const contentVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: { delay: 0.1 + i * 0.05, duration: 0.4 }
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
            <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
          </div>
        )}

        <img
          src={src}
          loading="lazy"
          onLoad={() => setLoaded(true)}
          className={`
                        max-h-[300px]
                        w-auto
                        max-w-full
                        object-contain
                        rounded-xl
                        border border-white/10
                        transition-opacity duration-300
                        ${loaded ? "opacity-100" : "opacity-0"}
                    `}
          alt="Verified content"
        />
      </div>
    );
  }

  const handleRecheckConfirm = async () => {
    if (!currentData) return;

    try {
      setRecheckLoading(true);
      setRecheckMsg("");

      const endpoint = currentData.type === "image" ? "/image/remove" : "/text/remove";
      const api = `${urlBase}${endpoint}`;

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
      console.log("[Recheck failed]", err);
      setRecheckMsg(RECHECK_GENERIC_ERROR);
      setRecheckLoading(false);
    }
  };

  useEffect(() => {
    return onConnectionChange(setConnected);
  }, []);

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

  const showConnecting = !connected && !currentData && queue.length === 0;
  const showLoader = !currentData && queue.length === 0 && jobStore.hasJobs();

  if (showConnecting) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center gap-4 py-20">
        <Loader2 className="w-12 h-12 text-cyan-400 animate-spin" />
        <div className="text-gray-300 text-lg font-medium">
          Connecting to server…
        </div>
      </div>
    );
  }

  if (!currentData) {
    if (showLoader) {
      const jobs = jobStore.list();

      return (
        <div className="w-full h-full flex flex-col items-center justify-center gap-4 py-20">
          <Loader2 className="w-16 h-16 text-cyan-400 animate-spin" />
          <div className="text-gray-300 text-center space-y-2">
            <div className="text-xl font-semibold">Processing your content</div>
            <div className="text-cyan-400 text-sm font-mono">
              Job ID: {jobs[jobs.length - 1]}
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="w-full h-full flex flex-col items-center justify-center py-20">
        <motion.div
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          className="text-center space-y-6 max-w-2xl"
        >
          <div className="w-20 h-20 mx-auto rounded-2xl bg-linear-to-br from-cyan-500/20 to-blue-500/20 
                        border border-cyan-500/30 flex items-center justify-center">
            <span className="text-4xl">✓</span>
          </div>

          <div className="space-y-3">
            <h2 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 
                            bg-clip-text text-transparent">
              Welcome to SatyaMark
            </h2>
            <p className="text-gray-400 text-lg">
              Submit content below to verify its authenticity
            </p>
          </div>

          <div className="grid sm:grid-cols-2 gap-4 pt-4">
            <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-left">
              <div className="text-cyan-400 font-semibold mb-2">Text Verification</div>
              <p className="text-sm text-gray-400">
                Check factual accuracy and detect AI-generated text
              </p>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-left">
              <div className="text-blue-400 font-semibold mb-2">Image Verification</div>
              <p className="text-sm text-gray-400">
                Detect AI-generated or manipulated images
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  const markMeta = MARK_META[currentData.mark.toLowerCase()] || MARK_META["pending"];

  return (
    <>
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        className="w-full"
      >
        <div className="bg-slate-900/50 border border-white/10 rounded-2xl shadow-xl overflow-hidden">
          {/* Header Section */}
          <div className="bg-gradient-to-r from-slate-800 to-slate-900 border-b border-white/10 p-6">
            <motion.div
              custom={0}
              variants={contentVariants}
              initial="hidden"
              animate="visible"
              className="space-y-4"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-2">
                  <div className="text-sm text-gray-400 font-mono">
                    Verification ID: {currentData.dataId}
                  </div>
                  <div className="flex items-center gap-3">
                    <img
                      src={markMeta.icon}
                      alt={markMeta.label}
                      className="w-8 h-8 object-contain"
                    />
                    <span className={`text-2xl font-bold ${markMeta.color}`}>
                      {markMeta.label}
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-sm text-gray-400 mb-1">Confidence</div>
                  <div className="text-2xl font-bold text-green-400">
                    {currentData.confidence}%
                  </div>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Content Sections */}
          <div className="p-6 space-y-6">
            {/* Input Content */}
            {currentData.type === "text" && currentData.summary && (
              <motion.div
                custom={1}
                variants={contentVariants}
                initial="hidden"
                animate="visible"
                className="space-y-2"
              >
                <div className="text-xs uppercase tracking-wider text-cyan-400 font-semibold">
                  Submitted Content
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                  <div className="text-gray-200 leading-relaxed whitespace-pre-wrap">
                    {currentData.summary}
                  </div>
                </div>
              </motion.div>
            )}

            {currentData.type === "image" && currentData.image_url && (
              <motion.div
                custom={1}
                variants={contentVariants}
                initial="hidden"
                animate="visible"
                className="space-y-2"
              >
                <div className="text-xs uppercase tracking-wider text-cyan-400 font-semibold">
                  Submitted Image
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                  <LazyImage src={currentData.image_url} />
                </div>
              </motion.div>
            )}

            {/* Verification Result */}
            <motion.div
              custom={2}
              variants={contentVariants}
              initial="hidden"
              animate="visible"
              className="space-y-2"
            >
              <div className="text-xs uppercase tracking-wider text-cyan-400 font-semibold">
                Verification Analysis
              </div>
              <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                <div className="text-gray-200 leading-relaxed whitespace-pre-wrap">
                  {currentData.reason}
                </div>
              </div>
            </motion.div>

            {/* Sources */}
            {currentData.urls && currentData.urls.length > 0 && (
              <motion.div
                custom={3}
                variants={contentVariants}
                initial="hidden"
                animate="visible"
                className="space-y-2"
              >
                <div className="text-xs uppercase tracking-wider text-cyan-400 font-semibold">
                  Sources ({currentData.urls.length})
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                  <div className="space-y-2">
                    {currentData.urls.map((url, i) => (
                      <a
                        key={i}
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-start gap-2 text-cyan-400 hover:text-cyan-300 
                                                    transition-colors group"
                      >
                        <ExternalLink size={16} className="mt-1 shrink-0" />
                        <span className="break-all text-sm group-hover:underline">
                          {url}
                        </span>
                      </a>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="border-t border-white/10 bg-slate-900/50 p-4 flex flex-wrap items-center justify-between gap-3">
            <button
              onClick={() => setShowRecheckPopup(true)}
              className="inline-flex items-center gap-2 px-4 py-2 
                                bg-orange-500/10 hover:bg-orange-500/20 
                                border border-orange-500/30 hover:border-orange-500/50
                                text-orange-400 font-medium rounded-lg 
                                transition-all duration-200"
            >
              <RotateCcw size={16} />
              Request Recheck
            </button>

            <div className="flex items-center gap-3">
              {jobStore.hasJobs() && (
                <div className="flex items-center gap-2 px-4 py-2 
                                    bg-cyan-500/10 border border-cyan-500/30 
                                    rounded-lg text-sm">
                  <Loader2 size={16} className="text-cyan-400 animate-spin" />
                  <span className="text-cyan-400 font-medium">
                    Processing…
                  </span>
                </div>
              )}

              {queue.length > 0 && (
                <button
                  onClick={loadNext}
                  className="inline-flex items-center gap-2 px-4 py-2 
                                        bg-gradient-to-r from-cyan-600 to-blue-600 
                                        hover:from-cyan-500 hover:to-blue-500
                                        text-white font-semibold rounded-lg 
                                        shadow-lg shadow-cyan-500/25 
                                        transition-all duration-200"
                >
                  Load Next ({queue.length})
                  <ChevronRight size={16} />
                </button>
              )}
            </div>
          </div>
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
