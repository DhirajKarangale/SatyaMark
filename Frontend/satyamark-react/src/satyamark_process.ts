import { sendData } from "./satyamark_connect";

const mergeText = (texts: string[]) => texts.join(", ");

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

export async function process(divRef: HTMLDivElement, dataId: string) {
    const { text, images } = extractFromDiv(divRef);

    const mergedText = mergeText(text);
    const validImage = await getFirstValidImage(images);

    const jobId = sendData(mergedText, validImage ?? "", dataId);

    return jobId;
}

export async function process_satyamark(text: string, images: string, dataId: string) {
    const jobId = sendData(text, images ?? "", dataId);
    return jobId;
}