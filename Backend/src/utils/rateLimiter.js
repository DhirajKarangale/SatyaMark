const LIMIT = 100;
const WINDOW = 10_000;
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

function startCleanup() {
  setInterval(cleanup, CLEANUP_INTERVAL);
}

module.exports = { isAllowed, startCleanup };
