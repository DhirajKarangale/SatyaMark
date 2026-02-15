const crypto = require("crypto");

function generateSessionId(app_id) {
  const timestamp = Date.now();
  const random = crypto.randomBytes(8).toString("hex");
  return `${app_id}_${timestamp}_${random}`;
}

module.exports = { generateSessionId }