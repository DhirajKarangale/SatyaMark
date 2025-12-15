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
    if (images && !await isValidImageUrl(images)) {
        throw new Error("Image URL Not valid");
    }

    if (text && text.length < 3) {
        throw new Error("Text not valid");
    }

    if (!text && !images) {
        throw new Error("Text or images not valid");
    }

    const jobId = sendData(text, images ?? "", dataId);
    return jobId;
}