const crypto = require("crypto");

function normalizeText(str) {
    if (!str) return "";

    let text = str;

    // text = text.replace(/<[^>]*>/g, " ");

    // text = text
    //     .replace(/\*\*(.*?)\*\*/g, " $1 ")
    //     .replace(/\*(.*?)\*/g, " $1 ")
    //     .replace(/__(.*?)__/g, " $1 ")
    //     .replace(/_(.*?)_/g, " $1 ");

    text = text.toLowerCase();
    text = text.trim();
    // text = text.replace(/\s+/g, " ").trim();

    return text;
}

function normalizeText2(str) {
    if (!str) return "";

    let text = str;

    // Remove HTML
    text = text.replace(/<[^>]*>/g, " ");

    // Remove markdown
    text = text
        .replace(/\*\*(.*?)\*\*/g, " $1 ")
        .replace(/\*(.*?)\*/g, " $1 ")
        .replace(/__(.*?)__/g, " $1 ")
        .replace(/_(.*?)_/g, " $1 ");

    // Unicode normalize
    text = text.normalize("NFKC");

    // Lowercase
    text = text.toLowerCase();

    // Remove punctuation
    text = text.replace(/[^\p{L}\p{N}\s]/gu, " ");

    // Collapse whitespace
    text = text.replace(/\s+/g, " ").trim();

    return text;
}

function createHash(str) {
    const normalize = normalizeText(str);
    return crypto.createHash("sha256").update(normalize, "utf8").digest("hex");
}

function generateTextHashes(input) {
    const text_hash = createHash(input);
    const normalized = normalizeText2(input);
    const summary_hash = createHash(normalized);

    return {
        text_hash,
        summary_hash,
    };
}

module.exports = { generateTextHashes }