const crypto = require("crypto");
const { URL } = require("url");

async function generateImageHash(imageUrl) {
    let parsedUrl;
    try {
        parsedUrl = new URL(imageUrl);
    } catch {
        console.log("Invalid URL");
        return;
    }

    if (!["http:", "https:"].includes(parsedUrl.protocol)) {
        console.log("Only HTTP/HTTPS URLs are allowed");
        return;
    }

    const response = await fetch(imageUrl);

    if (!response.ok) {
        console.log(`Failed to download image: ${response.status} ${response.statusText}`);
        return;
    }

    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    if (!buffer.length) {
        console.log("Downloaded image is empty");
        return;
    }

    const hash = crypto.createHash("sha256").update(buffer).digest("hex");

    return hash;
}

module.exports = { generateImageHash };
