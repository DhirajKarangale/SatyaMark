const EventEmitter = require("events");
const { getClients } = require("../redis/redisClient");

const CHANNEL_NAME = "ws_callbacks";

class RedisEventBus extends EventEmitter {
  constructor() {
    super();
    this.isSubscribed = false;
  }

  async init() {
    const { sub } = getClients();
    if (!sub) {
      console.log("[RedisEventBus] No subscriber client available.");
      return;
    }

    try {
      await sub.subscribe(CHANNEL_NAME, (message) => {
        try {
          const parsed = JSON.parse(message);
          // Emit locally for ws-server.js to pick up and send to connected socket
          this.emit("sendData", parsed);
        } catch (err) {
          console.log("[RedisEventBus] Parse error:", err.message);
        }
      });
      this.isSubscribed = true;
      console.log(`[RedisEventBus] Subscribed to ${CHANNEL_NAME}`);
    } catch (err) {
      console.log("[RedisEventBus] Subscribe error:", err.message);
    }
  }

  async publishData({ clientId, payload }) {
    // Single-instance optimization: Bypass Redis Pub/Sub and emit locally
    this.emit("sendData", { clientId, payload });
  }
}

const redisEventBus = new RedisEventBus();

module.exports = redisEventBus;
