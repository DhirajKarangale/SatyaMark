const crypto = require("crypto");
const { URL } = require("url");
const fetch = require("node-fetch"); // REQUIRED

async function generateImageHash(imageUrl) {
  let parsedUrl;

  try {
    parsedUrl = new URL(imageUrl);
  } catch {
    throw new Error("Invalid image URL");
  }

  if (!["http:", "https:"].includes(parsedUrl.protocol)) {
    throw new Error("Only HTTP/HTTPS URLs are allowed");
  }

  const response = await fetch(imageUrl, { timeout: 10000 });

  if (!response.ok) {
    throw new Error(`Failed to download image: ${response.status}`);
  }

  const hash = crypto.createHash("sha256");

  await new Promise((resolve, reject) => {
    response.body.on("data", chunk => hash.update(chunk));
    response.body.on("end", resolve);
    response.body.on("error", reject);
  });

  return {
    image_hash: hash.digest("hex"),
  };
}

module.exports = { generateImageHash };
