const mergeText = (texts: string[]) => texts.join(" |#| ");

const isValidImageUrl = (url: string): Promise<boolean> => {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(true);
    img.onerror = () => resolve(false);
    img.src = url;
  });
};

const getFirstValidImage = async (urls: string[]) => {
  for (const url of urls) {
    if (await isValidImageUrl(url)) return url;
  }
  return null;
};

const extractFromDiv = (root: HTMLDivElement) => {
  const images = Array.from(root.querySelectorAll("img")).map(img => img.src);

  const text: string[] = [];
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);

  let node: Node | null;
  while ((node = walker.nextNode())) {
    const trimmed = node.textContent?.trim();
    if (trimmed) text.push(trimmed);
  }

  return { text, images };
};

export async function process_data(divRef: HTMLDivElement, dataId: string) {
  if (!dataId) {
    throw new Error("Satyamark: Invalid dataId");
  }
  
  if (!divRef) {
    throw new Error("Satyamark: Invalid root element");
  }

  const { text, images } = extractFromDiv(divRef);

  const mergedText = mergeText(text);
  const validImage = await getFirstValidImage(images);

  if (!mergedText && !validImage) {
    throw new Error("Satyamark: No valid text or image found in the element");
  }

  if (mergedText && mergedText.length < 3) {
    throw new Error("Satyamark: Extracted text is too short");
  }

  const image_url = validImage ? validImage : "";

  return { text: mergedText, image_url: image_url }
}