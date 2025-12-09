import { onReceive } from "./satyamark_connect";

type StatusOptions = {
    iconSize?: number;
};

type JobEntry = {
    root: HTMLElement;
    iconSize: number;
};

const jobMap: Record<string, JobEntry> = {};

const DEFAULT_ICON_SIZE = 20;

const iconMap: Record<string, string> = {
    correct: "/correct.png",
    incorrect: "/incorrect.png",
    insufficient: "/insufficient.png",
    ai: "/ai.png",
    real: "/real.png",
    subjective: "/subjective.png",
    pending: "/pending.png",
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

    updateIcon(jobId, "pending");
}

function updateIcon(jobId: string, mark: string) {
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
}

onReceive((data) => {
    if (!data?.jobId) return;
    updateIcon(data.jobId, data.mark?.toLowerCase() ?? "pending");
});
