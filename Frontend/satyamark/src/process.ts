import { sendData } from "./connect";

const mergeText = (texts: string[]) => texts.join(", ");

const isValidImageUrl = (url: string) => new Promise<boolean>(res => {
  if (typeof window === "undefined") return res(false);
  const img = new Image();
  img.onload = () => res(true);
  img.onerror = () => res(false);
  img.src = url;
});

const extractFromDiv = (root: HTMLDivElement) => {
  const images = Array.from(root.querySelectorAll("img")).map(i => i.src);
  const text: string[] = [];
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  let n: Node | null;
  while ((n = walker.nextNode())) {
    const t = n.textContent?.trim();
    if (t) text.push(t);
  }
  return { text, images };
};

const getFirstValidImage = async (urls: string[]) => {
  for (const u of urls) if (await isValidImageUrl(u)) return u;
  return null;
};

export async function process(root: HTMLDivElement, dataId: string) {
  const { text, images } = extractFromDiv(root);
  const merged = mergeText(text);
  const validImage = await getFirstValidImage(images);
  return sendData(merged, validImage ?? "", dataId);
}
