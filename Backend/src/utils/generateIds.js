const crypto = require("crypto");

function generateSessionId(appId) {
  const timestamp = Date.now();
  const random = crypto.randomBytes(8).toString("hex");
  return `${appId}_${timestamp}_${random}`;
}

module.exports = { generateSessionId }