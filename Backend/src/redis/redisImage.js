const redis = require("redis");
require("dotenv").config();

const imageRedis = redis.createClient({
  url: process.env.REDIS_IMAGE_URL,
  socket: { reconnectStrategy: r => Math.min(r * 100, 3000) },
});

imageRedis.on("error", e => console.log("Image Redis error:", e.message));
(async () => { if (!imageRedis.isOpen) await imageRedis.connect(); })();

module.exports = imageRedis;