const redis = require("redis");
require("dotenv").config();

const textRedis = redis.createClient({
  url: process.env.REDIS_TEXT_URL,
  socket: { reconnectStrategy: r => Math.min(r * 100, 3000) },
});

textRedis.on("error", e => {
  if (e.message.includes("Socket closed")) return;
  console.log("Text Redis error:", e.message)
});

const ready = textRedis.connect();

module.exports = { textRedis, ready };