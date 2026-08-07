const redisEventBus = require("../starter/redisEventBus");
const { getClients } = require("../redis/redisClient");

const LIMIT = 5;
const WINDOW_SEC = 15; // 15 seconds

async function isAllowed(id) {
  const { rateLimiter } = getClients();
  if (!rateLimiter) return true; // Fail open if no redis

  const key = `rate_limit:${id}`;
  const now = Date.now();
  const windowStart = now - (WINDOW_SEC * 1000);
  
  try {
    // Add current timestamp
    await rateLimiter.zAdd(key, { score: now, value: `${now}-${Math.random()}` });
    
    // Remove older timestamps
    await rateLimiter.zRemRangeByScore(key, 0, windowStart);
    
    // Get count
    const count = await rateLimiter.zCard(key);
    
    // Set expiry to window size so it cleans up itself
    await rateLimiter.expire(key, WINDOW_SEC);
    
    return count <= LIMIT;
  } catch (err) {
    console.log("[RateLimiter Error]", err.message);
    return true; // fail open
  }
}

async function emitRateLimitEvent(clientId, msg) {
  await redisEventBus.publishData({
    clientId,
    payload: {
      type: "RateLimiter",
      msg: msg
    }
  });
}

async function checkRateLimiter(clientId, dataSessionId, socketSessionId) {
  if (!socketSessionId || !dataSessionId) {
    await emitRateLimitEvent(clientId, "Session not established");
    return false;
  }
  
  if (dataSessionId !== socketSessionId) {
    await emitRateLimitEvent(clientId, "Invalid session");
    return false;
  }

  const allowed = await isAllowed(socketSessionId);
  if (!allowed) {
    await emitRateLimitEvent(clientId, "Rate limit exceeded");
    return false;
  }

  return true;
}

function startRateLimiterCleanup() {
  console.log("[RateLimiter] Cleanup is now handled natively by Redis expiration.");
}

module.exports = { checkRateLimiter, startRateLimiterCleanup };
