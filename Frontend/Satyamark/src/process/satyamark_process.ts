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
    if (!await isValidImageUrl(images)) return "Image URL Not valid";
    const jobId = sendData(text, images ?? "", dataId);
    return jobId;
}