import { onReceive } from "./satyamark_connect";
import { ICON_URLS, type IconKey } from "./utils/iconRegistry";
import { ensureIconLoaded } from "./utils/iconLoader";

type StatusOptions = {
    iconSize?: number;
};

type JobEntry = {
    root: HTMLElement;
    iconSize: number;
};

const jobMap: Record<string, JobEntry> = {};

const DEFAULT_ICON_SIZE = 20;
const satyamark_url = "https://satyamark.vercel.app/chat";

const iconMap = ICON_URLS;

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

function updateIcon(jobId: string, rawMark: string, data: any) {
    const entry = jobMap[jobId];
    if (!entry) return;

    const { root, iconSize } = entry;
    const mark: IconKey = rawMark in ICON_URLS ? (rawMark as IconKey) : "pending";
  
    ensureIconLoaded(mark);

    const container = root.querySelector("[data-satyamark-status-container]") as HTMLElement;
    if (!container) return;

    container.innerHTML = "";
    container.style.position = "relative";

    const icon = document.createElement("img");
    icon.alt = "status";
    icon.style.objectFit = "contain";
    icon.style.display = "block";
    icon.style.width = iconSize + "px";
    icon.style.height = iconSize + "px";
    icon.src = ICON_URLS[mark];
    container.appendChild(icon);

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
    icon.onmouseenter = () => { tooltip.style.opacity = "1"; };
    icon.onmouseleave = () => { tooltip.style.opacity = "0"; };

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