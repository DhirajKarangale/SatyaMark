const redis = require("redis");
require("dotenv").config();

const imageRedis = redis.createClient({
  url: process.env.REDIS_UPSTASH_IMAGE_URL,
  socket: { reconnectStrategy: r => Math.min(r * 100, 3000) },
});

imageRedis.on("error", e => {
  if (e.message.includes("Socket closed")) return;
  console.log("Image Redis error:", e.message)
});

const ready = imageRedis.connect();

module.exports = { imageRedis, ready };