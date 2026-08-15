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
      // We resolve instead of reject so Promise.all doesn't fail fast
      // if one icon fails to load.
      resolve(); 
    };
    img.src = ICON_URLS[key];
  });

  iconLoadMap.set(key, promise);
  return promise;
}

/**
 * Preload all icons immediately on init and return a Promise
 */
export function preloadIcons(): Promise<void[]> {
  const promises = (Object.keys(ICON_URLS) as IconKey[]).map(loadIcon);
  return Promise.all(promises);
}

/**
 * Ensure a specific icon is loaded (used during render)
 */
export function ensureIconLoaded(key: IconKey) {
  return loadIcon(key).catch(() => { });
}