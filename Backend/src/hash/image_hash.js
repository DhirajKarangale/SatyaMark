const crypto = require("crypto");
const { URL } = require("url");

async function generateImageHash(imageUrl) {
    let parsedUrl;
    try {
        parsedUrl = new URL(imageUrl);
    } catch {
        return null;
    }

    if (!["http:", "https:"].includes(parsedUrl.protocol)) {
        return null;
    }

    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 15000);

        const response = await fetch(imageUrl, { signal: controller.signal });
        clearTimeout(timeout);

        if (!response.ok) {
            return null;
        }

        const arrayBuffer = await response.arrayBuffer();
        const buffer = Buffer.from(arrayBuffer);

        if (!buffer.length) {
            return null;
        }

        const hash = crypto.createHash("sha256").update(buffer).digest("hex");
        return hash;
    } catch {
        return null;
    }
}

module.exports = { generateImageHash };
