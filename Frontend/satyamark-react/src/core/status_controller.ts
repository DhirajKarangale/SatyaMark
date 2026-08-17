import { ICON_URLS, type IconKey } from "../utils/iconRegistry";
import { ensureIconLoaded, preloadIcons } from "../utils/iconLoader";

const DEFAULT_ICON_SIZE = 20;
const satyamark_url = "https://satyamark.js.org/chat";

let areIconsLoaded = false;
type StatusQueueItem = {
    containerRef: HTMLDivElement;
    data: any;
};
const statusQueue: StatusQueueItem[] = [];

export async function initIcons() {
    await preloadIcons();
    areIconsLoaded = true;
    flushStatusQueue();
}

function flushStatusQueue() {
    while (statusQueue.length > 0) {
        const item = statusQueue.shift();
        if (item && document.body.contains(item.containerRef)) {
            updateIconImmediately(item.containerRef, item.data);
        }
    }
}

export function updateIcon(containerRef: HTMLDivElement, data: any) {
    if (!areIconsLoaded) {
        // Update data if container already exists in queue, otherwise push new
        const existingIndex = statusQueue.findIndex(item => item.containerRef === containerRef);
        if (existingIndex !== -1) {
            statusQueue[existingIndex].data = data;
        } else {
            statusQueue.push({ containerRef, data });
        }
        return;
    }
    updateIconImmediately(containerRef, data);
}

function updateIconImmediately(containerRef: HTMLDivElement, data: any) {
    const root = containerRef;
    const iconSize = DEFAULT_ICON_SIZE;
    let mark: IconKey = "pending";
    if (data && data.mark) mark = data.mark?.toLowerCase();

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
            const routeUrl = `${satyamark_url}/${type}/${data.dataId}`;
            window.open(routeUrl, "_blank");
        };
    } else {
        icon.style.cursor = "default";
        icon.onclick = null;
    }
}