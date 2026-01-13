import { ICON_URLS, type IconKey } from "./iconRegistry";

const iconLoadMap = new Map<IconKey, Promise<void>>();

function loadIcon(key: IconKey): Promise<void> {
  const existing = iconLoadMap.get(key);
  if (existing) return existing;

  const promise = new Promise<void>((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve();
    img.onerror = () => {
      iconLoadMap.delete(key); // allow retry
      reject(new Error(`Failed to load icon: ${key}`));
    };
    img.src = ICON_URLS[key];
  });

  iconLoadMap.set(key, promise);
  return promise;
}

/**
 * Background preload — non-blocking, idempotent
 */
export function preloadIcons() {
  const run = () => {
    (Object.keys(ICON_URLS) as IconKey[]).forEach(loadIcon);
  };

  if ("requestIdleCallback" in window) {
    (window as any).requestIdleCallback(run);
  } else {
    setTimeout(run, 0);
  }
}

/**
 * Ensure a specific icon is loaded (used during render)
 */
export function ensureIconLoaded(key: IconKey) {
  return loadIcon(key).catch(() => { });
}