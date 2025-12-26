const redis = require("redis");
require("dotenv").config();

const client = redis.createClient({
  url: process.env.REDIS_URL,
  socket: {
    reconnectStrategy: retries => Math.min(retries * 100, 3000),
  },
});

client.on("error", (err) => {
  console.log("Redis error:", err.message);
});

client.on("connect", () => {
  console.log("Redis connected");
});

client.on("reconnecting", () => {
  console.log("Redis reconnecting...");
});

(async () => {
  try {
    if (!client.isOpen) await client.connect();
  } catch (e) {
    console.log("Redis initial connect failed:", e);
  }
})();

module.exports = client;