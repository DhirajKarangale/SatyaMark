const eventBus = require("../starter/eventBus");

const LIMIT = 5;
const WINDOW = 15_000;
const CLEANUP_INTERVAL = 60 * 60 * 1000;

const requests = new Map();

function isAllowed(id) {
  const now = Date.now();
  const windowStart = now - WINDOW;

  if (!requests.has(id)) {
    requests.set(id, { timestamps: [], start: 0 });
  }

  const data = requests.get(id);

  while (
    data.start < data.timestamps.length &&
    data.timestamps[data.start] <= windowStart
  ) {
    data.start++;
  }

  const activeRequests = data.timestamps.length - data.start;

  if (activeRequests >= LIMIT) {
    return false;
  }

  data.timestamps.push(now);
  return true;
}

function cleanup() {
  const now = Date.now();
  const windowStart = now - WINDOW;

  for (const [id, data] of requests.entries()) {
    while (
      data.start < data.timestamps.length &&
      data.timestamps[data.start] <= windowStart
    ) {
      data.start++;
    }

    if (data.start >= data.timestamps.length) {
      requests.delete(id);
    } else if (data.start > 0) {
      data.timestamps = data.timestamps.slice(data.start);
      data.start = 0;
    }
  }
}

function emitRateLimitEvent(clientId, msg) {
  eventBus.emit("sendData", {
    clientId,
    payload: {
      type: "RateLimiter",
      msg: msg
    }
  });
}

function checkRateLimiter(clientId, dataSessionId, socketSessionId) {
  if (!socketSessionId || !dataSessionId) {
    emitRateLimitEvent(clientId, "Session not established");
    return false;
  }
  
  if (dataSessionId !== socketSessionId) {
    emitRateLimitEvent(clientId, "Invalid session");
    return false;
  }

  if (!isAllowed(socketSessionId)) {
    emitRateLimitEvent(clientId, "Rate limit exceeded");
    return false;
  }

  return true;
}

function startRateLimiterCleanup() {
  setInterval(cleanup, CLEANUP_INTERVAL);
}

module.exports = { checkRateLimiter, startRateLimiterCleanup };
