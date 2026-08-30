const redisEventBus = require("../starter/redisEventBus");
const { getClients } = require("../redis/redisClient");
const connectionManager = require("./connectionManager");

const LIMIT = 5;
const WINDOW_SEC = 15; // 15 seconds

// Issue 11: In-memory fallback rate limiter
const memoryStore = new Map();

const LUA_RATE_LIMIT = `
  local key = KEYS[1]
  local now = tonumber(ARGV[1])
  local windowStart = tonumber(ARGV[2])
  local limit = tonumber(ARGV[3])
  local windowSec = tonumber(ARGV[4])
  local randomVal = ARGV[5]

  redis.call('ZREMRANGEBYSCORE', key, 0, windowStart)
  local count = redis.call('ZCARD', key)

  if count < limit then
    redis.call('ZADD', key, now, randomVal)
    redis.call('EXPIRE', key, windowSec)
    return 1
  else
    return 0
  end
`;

function isAllowedInMemory(id) {
  const key = `rate_limit:${id}`;
  const now = Date.now();
  const windowStart = now - (WINDOW_SEC * 1000);

  let timestamps = memoryStore.get(key) || [];
  timestamps = timestamps.filter(t => t > windowStart);

  if (timestamps.length < LIMIT) {
    timestamps.push(now);
    memoryStore.set(key, timestamps);
    return true;
  }

  return false;
}

// Periodic cleanup of expired in-memory entries
setInterval(() => {
  const now = Date.now();
  const windowStart = now - (WINDOW_SEC * 1000);
  for (const [key, timestamps] of memoryStore.entries()) {
    const valid = timestamps.filter(t => t > windowStart);
    if (valid.length === 0) {
      memoryStore.delete(key);
    } else {
      memoryStore.set(key, valid);
    }
  }
}, 60000);

async function isAllowed(id) {
  const { rateLimiter } = getClients();

  // Issue 11: Use in-memory fallback when Redis is unavailable
  if (!rateLimiter || !connectionManager.isConnected("RateLimiter")) {
    return isAllowedInMemory(id);
  }

  const key = `rate_limit:${id}`;
  const now = Date.now();
  const windowStart = now - (WINDOW_SEC * 1000);
  const randomVal = `${now}-${Math.random()}`;
  
  try {
    const result = await rateLimiter.eval(LUA_RATE_LIMIT, {
      keys: [key],
      arguments: [now.toString(), windowStart.toString(), LIMIT.toString(), WINDOW_SEC.toString(), randomVal]
    });
    return result === 1;
  } catch (err) {
    console.log("[RateLimiter Error]", err.message);
    return isAllowedInMemory(id); // Fallback on error too
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

async function checkRateLimiter(clientId, socketSessionId) {
  if (!socketSessionId) {
    await emitRateLimitEvent(clientId, "Session not established");
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
  console.log("[RateLimiter] Cleanup handled by Redis expiration and in-memory periodic cleanup.");
}

module.exports = { checkRateLimiter, startRateLimiterCleanup };
