const redis = require("redis");
require("dotenv").config();

const textRedis = redis.createClient({
  url: process.env.REDIS_TEXT_URL,
  socket: { reconnectStrategy: r => Math.min(r * 100, 3000) },
});

textRedis.on("error", e => console.log("Text Redis error:", e.message));
(async () => { if (!textRedis.isOpen) await textRedis.connect(); })();

module.exports = textRedis;