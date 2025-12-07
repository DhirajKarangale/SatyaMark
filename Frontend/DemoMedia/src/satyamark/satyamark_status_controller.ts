import { onReceive } from "./satyamark_connect";

type StatusOptions = {
    iconSize?: number; // px
};

type JobEntry = {
    container: HTMLElement;
    iconSize: number;
};

const jobMap: Record<string, JobEntry> = {};

const DEFAULT_ICON_SIZE = 20; // <--- single source of truth

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
    const container = rootElement.querySelector("[data-status-container]") as HTMLElement;

    if (!container) {
        console.warn(`No [data-status-container] found for jobId ${jobId}`);
        return;
    }

    const iconSize = options.iconSize ?? DEFAULT_ICON_SIZE;

    jobMap[jobId] = {
        container,
        iconSize,
    };

    updateIcon(jobId, "pending");
}

function updateIcon(jobId: string, mark: string) {
    const entry = jobMap[jobId];
    if (!entry) return;

    const { container } = entry;
    const iconSize = entry.iconSize ?? DEFAULT_ICON_SIZE; // <--- enforce default again

    let icon = container.querySelector("img") as HTMLImageElement;

    if (!icon) {
        icon = document.createElement("img");
        icon.alt = "status";

        // INLINE CSS
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
