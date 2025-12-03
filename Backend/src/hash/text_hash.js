const crypto = require("crypto");

function normalizeText(str) {
    if (!str) return "";

    let text = str;

    text = text.replace(/<[^>]*>/g, " ");

    text = text
        .replace(/\*\*(.*?)\*\*/g, " $1 ")
        .replace(/\*(.*?)\*/g, " $1 ")
        .replace(/__(.*?)__/g, " $1 ")
        .replace(/_(.*?)_/g, " $1 ");

    text = text.toLowerCase();
    text = text.replace(/\s+/g, " ").trim();

    return text;
}

function createHash(str) {
    return crypto.createHash("sha256").update(str, "utf8").digest("hex");
}

function generateTextHashes(input) {
    const text_hash = createHash(input);
    const normalized = normalizeText(input);
    const summary_hash = createHash(normalized);

    return {
        text_hash,
        summary_hash,
    };
}

module.exports = { generateTextHashes }