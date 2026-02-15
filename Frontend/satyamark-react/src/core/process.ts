import { onMessage } from "./eventBus";
import { sendJob } from "./connectionManager";
import { updateIcon } from "./status_controller";
import { process_data } from "../utils/process_data";

const jobMap = new Map();

export async function process(containerRef: HTMLDivElement, dataId: string) {
    const { text, image_url } = await process_data(containerRef, dataId);
    const jobId = await sendJob(text, image_url, dataId);
    jobMap.set(jobId, containerRef);
    updateIcon(containerRef, null);
    return jobId;
}

onMessage((data) => {
    if (!data || !data.jobId) return;
    const containerRef = jobMap.get(data.jobId);
    if (!containerRef) return;
    updateIcon(containerRef, data);
});