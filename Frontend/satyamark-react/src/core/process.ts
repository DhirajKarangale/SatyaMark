import { onMessage } from "./eventBus";
import { onConnected } from "./eventBus";
import { sendJob } from "./connectionManager";
import { updateIcon } from "./status_controller";
import { process_data } from "../utils/process_data";
import { generateHash } from "../utils/hash";
import { sendTraceEvent, flushTrace } from "../utils/tracer";

let isConnected = false;
let isSendingJobs = false;

// Issue 27: LRU cache with max size
const MAX_CACHE_SIZE = 500;

type JobInfo = {
    containerRef: HTMLDivElement;
    dataId: string;
    hash?: string;
};

const jobMap = new Map<string, JobInfo>();

const verificationCache = new Map<string, any>();
const containerObservers = new WeakMap<HTMLDivElement, MutationObserver>();
const currentHashes = new WeakMap<HTMLDivElement, string>();
const debounceTimers = new WeakMap<HTMLDivElement, ReturnType<typeof setTimeout>>();
const containerLoadHandlers = new WeakMap<HTMLDivElement, EventListener>();

type ProcessQueueItem = {
    containerRef: HTMLDivElement;
    dataId: string;
};

const process_queue: ProcessQueueItem[] = [];

// Issue 27: Cache with FIFO eviction at max size
function cacheSet(key: string, value: any) {
    if (verificationCache.size >= MAX_CACHE_SIZE) {
        const oldestKey = verificationCache.keys().next().value;
        if (oldestKey !== undefined) {
            verificationCache.delete(oldestKey);
        }
    }
    verificationCache.set(key, value);
}

// Issue 26: Return cleanup function to disconnect observer and free resources
export function process(containerRef: HTMLDivElement, dataId: string): () => void {
    validateStatusContainer(containerRef);
    setupObserver(containerRef, dataId);
    void queueProcessing(containerRef, dataId);

    return () => {
        const observer = containerObservers.get(containerRef);
        if (observer) {
            observer.disconnect();
            containerObservers.delete(containerRef);
        }
        const timer = debounceTimers.get(containerRef);
        if (timer) clearTimeout(timer);
        debounceTimers.delete(containerRef);
        
        const loadHandler = containerLoadHandlers.get(containerRef);
        if (loadHandler) {
            containerRef.removeEventListener('load', loadHandler, true);
            containerLoadHandlers.delete(containerRef);
        }
        
        currentHashes.delete(containerRef);
    };
}

function setupObserver(containerRef: HTMLDivElement, dataId: string) {
    if (containerObservers.has(containerRef)) return;

    const observer = new MutationObserver((mutations) => {
        const statusContainer = containerRef.querySelector("[data-satyamark-status-container]");
        
        const isOnlyStatusUpdate = mutations.every(mutation => {
            return statusContainer && statusContainer.contains(mutation.target);
        });

        if (isOnlyStatusUpdate) {
            return;
        }

        const existingTimer = debounceTimers.get(containerRef);
        if (existingTimer) clearTimeout(existingTimer);

        const timer = setTimeout(() => {
            void queueProcessing(containerRef, dataId);
        }, 500);

        debounceTimers.set(containerRef, timer);
    });

    observer.observe(containerRef, {
        childList: true,
        characterData: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['src', 'alt', 'srcset'],
    });

    containerObservers.set(containerRef, observer);

    const loadHandler = (e: Event) => {
        if (e.target instanceof HTMLImageElement && containerRef.contains(e.target)) {
            const existingTimer = debounceTimers.get(containerRef);
            if (existingTimer) clearTimeout(existingTimer);
            const timer = setTimeout(() => {
                void queueProcessing(containerRef, dataId);
            }, 500);
            debounceTimers.set(containerRef, timer);
        }
    };

    containerRef.addEventListener('load', loadHandler, true);
    containerLoadHandlers.set(containerRef, loadHandler);
}

// Issue 17: generateHash is now async (SHA-256)
async function queueProcessing(containerRef: HTMLDivElement, dataId: string) {
    try {
        const { text, image_url } = await process_data(containerRef, dataId);
        const contentHash = await generateHash(text + image_url);

        const currentHash = currentHashes.get(containerRef);
        if (currentHash === contentHash) {
            return;
        }

        currentHashes.set(containerRef, contentHash);

        if (verificationCache.has(contentHash)) {
            const cachedData = verificationCache.get(contentHash);
            updateIcon(containerRef, cachedData);
            return;
        }

        sendTraceEvent({
            component: "frontend",
            stage: "verification",
            event: "verification_started",
            details: { dataId }
        });

        updateIcon(containerRef, { mark: "pending" });

        process_queue.push({ containerRef, dataId });
        void sendJobs();

    } catch (error) {
        console.error("Satyamark: Failed to prepare item for processing:", error);
    }
}

function validateStatusContainer(containerRef: HTMLDivElement): void {
    const statusContainer = containerRef.querySelector(
        "[data-satyamark-status-container]"
    );

    if (!statusContainer) {
        throw new Error(
            'Satyamark: Missing element with attribute "data-satyamark-status-container" inside containerRef.'
        );
    }
}

async function sendJobs(): Promise<void> {
    if (isSendingJobs || !isConnected) return;

    isSendingJobs = true;

    while (process_queue.length > 0) {
        const item = process_queue[0];
        if (!item) break;

        const { containerRef, dataId } = item;
        const contentHash = currentHashes.get(containerRef);

        try {
            const { text, image_url } = await process_data(containerRef, dataId);

            const newContentHash = await generateHash(text + image_url);
            if (newContentHash !== contentHash) {
                process_queue.shift();
                continue;
            }

            const jobId: string = await sendJob(text, image_url, dataId);
            
            sendTraceEvent({
                jobId,
                component: "frontend",
                stage: "verification_submission",
                event: "request_payload_prepared",
                details: { dataId, has_image: !!image_url, text_length: text?.length }
            });

            sendTraceEvent({
                jobId,
                component: "frontend",
                stage: "verification_submission",
                event: "request_sent",
                details: {}
            });

            jobMap.set(jobId, { containerRef, dataId, hash: contentHash });
            process_queue.shift();
        } catch (error) {
            if (error instanceof Error && error.message === "notready") {
                isSendingJobs = false;

                setTimeout(() => {
                    void sendJobs();
                }, 1000);

                return;
            }

            console.error("Satyamark: Failed to process item:", error);
            process_queue.shift();
        }
    }

    isSendingJobs = false;
}

onMessage((data) => {
    console.log("SatyaMark WebSocket received data:", data);

    if (!data || !data.jobId) return;

    sendTraceEvent({
        jobId: data.jobId,
        component: "frontend",
        stage: "ui_update",
        event: "websocket_result_received",
        details: { mark: data.mark, confidence: data.confidence }
    });

    const jobInfo = jobMap.get(data.jobId);

    if (!jobInfo) return;

    jobMap.delete(data.jobId);
    const { containerRef, dataId: fallbackDataId, hash } = jobInfo;

    if (document.body.contains(containerRef)) {
        const currentDataId = containerRef.dataset.currentDataId;
        const finalDataId = data.dataId || currentDataId || fallbackDataId;

        if (data.dataId) containerRef.dataset.currentDataId = data.dataId;

        console.log("SatyaMark process.ts - Final dataId used for updateIcon:", finalDataId);

        const finalData = { ...data, dataId: finalDataId };

        if (hash) {
            cacheSet(hash, finalData);
        }

        if (currentHashes.get(containerRef) === hash) {
            updateIcon(containerRef, finalData);
        }
        
        sendTraceEvent({
            jobId: data.jobId,
            component: "frontend",
            stage: "ui_update",
            event: "ui_update_completed",
            details: { mark: finalData.mark }
        });
        
        flushTrace(data.jobId);
    }
});

onConnected((data: any) => {
    isConnected = !!data;
    if (isConnected) {
        void sendJobs();
    }
});