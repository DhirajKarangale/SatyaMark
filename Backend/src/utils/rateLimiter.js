const redisEventBus = require("../starter/redisEventBus");
const { getClients } = require("../redis/redisClient");

const LIMIT = 5;
const WINDOW_SEC = 15; // 15 seconds

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

async function isAllowed(id) {
  const { rateLimiter } = getClients();
  if (!rateLimiter) return true; // Fail open if no redis

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
  console.log("[RateLimiter] Cleanup is now handled natively by Redis expiration.");
}

module.exports = { checkRateLimiter, startRateLimiterCleanup };
