require("dotenv").config();
const redis = require("redis");

const clients = {
  renderText: null,
  upstashText: null,
  renderImage: null,
  upstashImage: null,
  pub: null,
  sub: null,
  // Single generic client for rate limiting (can be same as renderText)
  rateLimiter: null 
};

async function createAndConnect(url, name) {
  if (!url) return null;
  const client = redis.createClient({ url });
  client.on("error", (err) => console.log(`[Redis Error - ${name}]`, err.message));
  // client.on("ready", () => console.log(`[Redis Ready - ${name}]`));
  try {
    await client.connect();
  } catch (err) {
    console.log(`[Redis Connect Error - ${name}]`, err.message);
  }
  return client;
}

async function initRedisClients() {
  console.log("[Redis] Initializing persistent connections...");
  
  clients.renderText = await createAndConnect(process.env.REDIS_RENDER_TEXT_URL, "Render Text");
  clients.upstashText = await createAndConnect(process.env.REDIS_UPSTASH_TEXT_URL, "Upstash Text");
  clients.renderImage = await createAndConnect(process.env.REDIS_RENDER_IMAGE_URL, "Render Image");
  clients.upstashImage = await createAndConnect(process.env.REDIS_UPSTASH_IMAGE_URL, "Upstash Image");

  // Use the most available URL for Pub/Sub and Rate Limiting
  const primaryUrl = process.env.REDIS_RENDER_TEXT_URL || process.env.REDIS_UPSTASH_TEXT_URL;
  
  clients.pub = await createAndConnect(primaryUrl, "Publisher");
  clients.sub = await createAndConnect(primaryUrl, "Subscriber");
  clients.rateLimiter = await createAndConnect(primaryUrl, "RateLimiter");

  console.log("[Redis] Initialization complete.");
}

function getClients() {
  return clients;
}

module.exports = { initRedisClients, getClients };
