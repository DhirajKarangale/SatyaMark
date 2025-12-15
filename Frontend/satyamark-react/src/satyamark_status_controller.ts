import { onReceive } from "./satyamark_connect";

import correctIcon from "../icons-mark/correct.png";
import incorrectIcon from "../icons-mark/incorrect.png";
import insufficientIcon from "../icons-mark/insufficient.png";
import aiIcon from "../icons-mark/ai.png";
import realIcon from "../icons-mark/real.png";
import subjectiveIcon from "../icons-mark/subjective.png";
import pendingIcon from "../icons-mark/pending.png";

type StatusOptions = {
    iconSize?: number;
};

type JobEntry = {
    root: HTMLElement;
    iconSize: number;
};

const jobMap: Record<string, JobEntry> = {};

const DEFAULT_ICON_SIZE = 20;
const satyamark_url = "http://localhost:5173";

const iconMap: Record<string, string> = {
    correct: correctIcon,
    incorrect: incorrectIcon,
    insufficient: insufficientIcon,
    ai: aiIcon,
    real: realIcon,
    subjective: subjectiveIcon,
    pending: pendingIcon,
};

export function registerStatus(
    jobId: string,
    rootElement: HTMLElement,
    options: StatusOptions = {}
) {
    jobMap[jobId] = {
        root: rootElement,
        iconSize: options.iconSize ?? DEFAULT_ICON_SIZE,
    };

    updateIcon(jobId, "pending", null);
}

function updateIcon(jobId: string, mark: string, data: any) {
    const entry = jobMap[jobId];
    if (!entry) return;

    const { root, iconSize } = entry;

    const container = root.querySelector("[data-status-container]") as HTMLElement;
    if (!container) return;

    let icon = container.querySelector("img") as HTMLImageElement;

    if (!icon) {
        icon = document.createElement("img");
        icon.alt = "status";
        icon.style.objectFit = "contain";
        icon.style.display = "block";
        container.appendChild(icon);
    }

    icon.style.width = iconSize + "px";
    icon.style.height = iconSize + "px";
    icon.src = iconMap[mark] || iconMap["pending"];

    const type = data?.type;
    const isValidType = type === "text" || type === "image";
    const isClickable = !!data?.dataId && isValidType && mark !== "pending";

    if (isClickable) {
        icon.style.cursor = "pointer";
        icon.onclick = () => {
            window.open(
                `${satyamark_url}/${type}/${data.dataId}`,
                "_blank"
            );
        };
    } else {
        icon.style.cursor = "default";
        icon.onclick = null;
    }
}

onReceive((data) => {
    if (!data?.jobId) return;
    updateIcon(data.jobId, data.mark?.toLowerCase() ?? "pending", data);
});