import { sendData } from "./satyamark_connect";

const isValidImageUrl = (url: string): Promise<boolean> => {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(true);
        img.onerror = () => resolve(false);
        img.src = url;
    });
};

// const getFirstValidImage = async (urls: string[]) => {
//     for (const url of urls) {
//         if (await isValidImageUrl(url)) return url;
//     }
//     return null;
// };

export async function process(text: string, images: string, dataId: string) {
    if (!text && !images) {
        throw new Error("Provide text or an image URL");
    }

    if (text && text.trim().length < 3) {
        throw new Error("Text must be at least 3 characters long");
    }

    if (images && !(await isValidImageUrl(images))) {
        throw new Error("Invalid image URL");
    }

    const jobId = await sendData(text, images ?? "", dataId);
    return jobId;
}