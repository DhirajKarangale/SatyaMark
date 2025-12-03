const crypto = require("crypto");
const { URL } = require("url");

async function generateImageHash(imageUrl) {
    try {
        let parsedUrl;
        try {
            parsedUrl = new URL(imageUrl);
        } catch {
            throw new Error("Invalid URL");
        }

        if (!["http:", "https:"].includes(parsedUrl.protocol)) {
            throw new Error("Only HTTP/HTTPS URLs are allowed");
        }

        const response = await fetch(imageUrl);

        if (!response.ok) {
            throw new Error(`Failed to download image: ${response.status} ${response.statusText}`);
        }

        const arrayBuffer = await response.arrayBuffer();
        const buffer = Buffer.from(arrayBuffer);

        if (!buffer.length) {
            throw new Error("Downloaded image is empty");
        }

        const hash = crypto.createHash("sha256").update(buffer).digest("hex");

        return { image_hash: hash };
    } catch (err) {
        return { error: err.message };
    }
}

module.exports = { generateImageHash };
