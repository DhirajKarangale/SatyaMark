const crypto = require("crypto");

function generateSessionId(app_id) {
  const time = Date.now().toString(36);
  const random = crypto.getRandomValues(new Uint32Array(1))[0].toString(36);
  return `${app_id}_${time}_${random}`;
}

module.exports = { generateSessionId }