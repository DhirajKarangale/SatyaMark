const mergeText = (texts: string[]) => texts.join(" |#| ");

const extractFromDiv = (root: HTMLDivElement) => {
  const statusContainer = root.querySelector("[data-satyamark-status-container]");

  const images = Array.from(root.querySelectorAll("img"))
    .filter(img => img.complete && img.naturalHeight > 0 && (!statusContainer || !statusContainer.contains(img)))
    .map(img => img.src);

  const text: string[] = [];
  const walker = document.createTreeWalker(
      root, 
      NodeFilter.SHOW_TEXT,
      {
          acceptNode: (node) => {
              if (statusContainer && statusContainer.contains(node)) {
                  return NodeFilter.FILTER_REJECT;
              }
              return NodeFilter.FILTER_ACCEPT;
          }
      }
  );

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
  const validImage = images.length > 0 ? images[0] : null;

  if (!mergedText && !validImage) {
    throw new Error("Satyamark: No valid text or image found in the element");
  }

  if (mergedText && mergedText.length < 3) {
    throw new Error("Satyamark: Extracted text is too short");
  }

  const image_url = validImage ? validImage : "";

  return { text: mergedText, image_url: image_url }
}