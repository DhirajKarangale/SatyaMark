import { onReceive } from "./satyamark_connect";

import verifyableIcon from "../icons-mark/verifyable.png";
import unverifyableIcon from "../icons-mark/unverifyable.png";
import insufficientIcon from "../icons-mark/insufficient.png";
import correctIcon from "../icons-mark/correct.png";
import incorrectIcon from "../icons-mark/incorrect.png";
import pendingIcon from "../icons-mark/pending.png";
import aiIcon from "../icons-mark/ai.png";
import nonaiIcon from "../icons-mark/nonai.png";

type StatusOptions = {
    iconSize?: number;
};

type JobEntry = {
    root: HTMLElement;
    iconSize: number;
};

const jobMap: Record<string, JobEntry> = {};

const DEFAULT_ICON_SIZE = 20;
const satyamark_url = "https://satyamark.vercel.app/";

const iconMap: Record<string, string> = {
    verifyable: verifyableIcon,
    unverifyable: unverifyableIcon,
    insufficient: insufficientIcon,
    correct: correctIcon,
    incorrect: incorrectIcon,
    pending: pendingIcon,
    ai: aiIcon,
    nonai: nonaiIcon,
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

    const container = root.querySelector("[data-satyamark-status-container]") as HTMLElement;
    if (!container) return;

    container.style.position = "relative";
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

    let tooltip = container.querySelector(".satyamark-tooltip") as HTMLDivElement;

    if (!tooltip) {
        tooltip = document.createElement("div");
        tooltip.style.position = "absolute";
        tooltip.style.top = `${icon.offsetTop - 6}px`;
        tooltip.style.left = `${icon.offsetLeft + icon.offsetWidth / 2}px`;
        tooltip.style.transform = "translate(-50%, -100%)";
        tooltip.style.background = "rgba(0,0,0,0.85)";
        tooltip.style.color = "#fff";
        tooltip.style.padding = "4px 8px";
        tooltip.style.borderRadius = "6px";
        tooltip.style.fontSize = "11px";
        tooltip.style.whiteSpace = "nowrap";
        tooltip.style.pointerEvents = "none";
        tooltip.style.opacity = "0";
        tooltip.style.transition = "opacity 0.15s ease";
        container.appendChild(tooltip);
    }

    tooltip.textContent = mark.toUpperCase();

    if (isClickable) {
        icon.style.cursor = "pointer";

        icon.onmouseenter = () => { tooltip.style.opacity = "1"; };
        icon.onmouseleave = () => { tooltip.style.opacity = "0"; };

        icon.onclick = () => {
            window.open(
                `${satyamark_url}/${type}/${data.dataId}`,
                "_blank"
            );
        };
    } else {
        icon.style.cursor = "default";
        icon.onclick = null;
        icon.onmouseenter = null;
        icon.onmouseleave = null;
        tooltip.style.opacity = "0";
    }
}

onReceive((data) => {
    if (!data?.jobId) return;
    updateIcon(data.jobId, data.mark?.toLowerCase() ?? "pending", data);
});