import { onMessage } from "./eventBus";
import { onConnected } from "./eventBus";
import { sendJob } from "./connectionManager";
import { updateIcon } from "./status_controller";
import { process_data } from "../utils/process_data";

let isConnected = false;
let isSendingJobs = false;

const jobMap = new Map<string, { containerRef: HTMLDivElement, dataId: string }>();

type ProcessQueueItem = {
    containerRef: HTMLDivElement;
    dataId: string;
};

const process_queue: ProcessQueueItem[] = [];

export function process(containerRef: HTMLDivElement, dataId: string) {
    validateStatusContainer(containerRef);

    const queueItem = process_queue.find(item => item.dataId === dataId);
    if (queueItem) {
        queueItem.containerRef = containerRef;
        return;
    }

    let foundInMap = false;
    for (const job of jobMap.values()) {
        if (job.dataId === dataId) {
            job.containerRef = containerRef;
            foundInMap = true;
            break;
        }
    }
    if (foundInMap) return;

    process_queue.push({ containerRef, dataId });
    void sendJobs();
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

        try {
            const { text, image_url } = await process_data(containerRef, dataId);
            const jobId: string = await sendJob(text, image_url, dataId);

            jobMap.set(jobId, { containerRef, dataId });
            process_queue.shift();
            updateIcon(containerRef, null);
        } catch (error) {
            if (error instanceof Error && error.message === "notready") {
                isSendingJobs = false;

                setTimeout(() => {
                    void sendJobs();
                }, 1000);

                return;
            }

            // Catch all other processing errors, log, and move to next item
            console.error("Satyamark: Failed to process item:", error);
            process_queue.shift();
        }
    }

    isSendingJobs = false;
}

onMessage((data) => {
    console.log("SatyaMark WebSocket received data:", data);

    if (!data || !data.jobId) return;

    const jobInfo = jobMap.get(data.jobId);

    if (!jobInfo) return;

    jobMap.delete(data.jobId);
    const { containerRef, dataId: fallbackDataId } = jobInfo;

    if (document.body.contains(containerRef)) {
        const currentDataId = containerRef.dataset.currentDataId;
        const finalDataId = data.dataId || currentDataId || fallbackDataId;

        if (data.dataId) containerRef.dataset.currentDataId = data.dataId;

        console.log("SatyaMark process.ts - Final dataId used for updateIcon:", finalDataId);

        updateIcon(containerRef, { ...data, dataId: finalDataId });
    }
});

onConnected((data: any) => {
    isConnected = !!data;
    if (isConnected) {
        void sendJobs();
    }
})