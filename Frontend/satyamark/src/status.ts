import { onReceive } from "./connect";
type StatusOptions = { iconSize?: number };
const DEFAULT_ICON_SIZE = 20;
const ICONS: Record<string, string> = {
  correct: "/correct.png", incorrect: "/incorrect.png", insufficient: "/insufficient.png",
  ai: "/ai.png", real: "/real.png", subjective: "/subjective.png", pending: "/pending.png"
};

type JobEntry = { root: HTMLElement; iconSize: number };
const jobMap: Record<string, JobEntry> = {};

export function registerStatus(jobId: string, root: HTMLElement, options: StatusOptions = {}) {
  jobMap[jobId] = { root, iconSize: options.iconSize ?? DEFAULT_ICON_SIZE };
  updateIcon(jobId, "pending");
}

function updateIcon(jobId: string, mark: string) {
  const entry = jobMap[jobId]; if (!entry) return;
  const { root, iconSize } = entry;
  const container = root.querySelector("[data-status-container]") as HTMLElement; if (!container) return;
  let icon = container.querySelector("img") as HTMLImageElement | null;
  if (!icon) { icon = document.createElement("img"); icon.alt = "status"; icon.style.objectFit = "contain"; icon.style.display = "block"; container.appendChild(icon); }
  icon.style.width = icon.style.height = iconSize + "px"; icon.src = ICONS[mark] || ICONS.pending;
}

onReceive((d) => { if (!d?.jobId) return; updateIcon(d.jobId, (d.mark || "pending").toLowerCase()); });
