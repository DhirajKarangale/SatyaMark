import { onMessage } from "./eventBus";
import { onConnected } from "./eventBus";
import { sendJob } from "./connectionManager";
import { updateIcon } from "./status_controller";
import { process_data } from "../utils/process_data";

let isConnected = false;
let isSendingJobs = false;

const jobMap = new Map<string, HTMLDivElement>();

type ProcessQueueItem = {
    containerRef: HTMLDivElement;
    dataId: string;
};

const process_queue: ProcessQueueItem[] = [];

export function process(containerRef: HTMLDivElement, dataId: string) {
    process_queue.push({ containerRef, dataId });
    void sendJobs();
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

            jobMap.set(jobId, containerRef);
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

            throw error;
        }
    }

    isSendingJobs = false;
}

onMessage((data) => {
    if (!data || !data.jobId) return;

    const containerRef = jobMap.get(data.jobId);

    if (!containerRef) return;

    jobMap.delete(data.jobId);
    updateIcon(containerRef, data);
});

onConnected((data: any) => {
    isConnected = !!data;
    if (isConnected) {
        void sendJobs();
    }
})