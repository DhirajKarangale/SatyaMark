require("dotenv").config();
const redis = require("redis");
const connectionManager = require("../utils/connectionManager");

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

function createProxyClient(client, name) {
    return new Proxy(client, {
        get(target, prop, receiver) {
            const originalProperty = target[prop];
            if (typeof originalProperty === 'function') {
                const isEventEmitterMethod = ['on', 'once', 'emit', 'removeListener', 'removeAllListeners'].includes(prop);

                if (!isEventEmitterMethod) {
                    return async function (...args) {
                        await connectionManager.ensureConnection(name);
                        return originalProperty.apply(target, args);
                    };
                }
                return originalProperty.bind(target);
            }
            return Reflect.get(target, prop, receiver);
        }
    });
}

async function createAndConnect(url, name) {
    if (!url) return null;
    const client = redis.createClient({
        url,
        pingInterval: 10000,
        socket: {
            connectTimeout: 10000,
            keepAlive: 10000,
            reconnectStrategy: (retries) => {
                if (retries > 20) {
                    console.error(`[CRITICAL] Max Redis reconnection attempts reached. Restarting server to recover...`);
                    process.exit(1);
                }
                return Math.min(retries * 500, 30000);
            }
        },
        disableOfflineQueue: true
    });

    connectionManager.setStatus(name, "connecting");

    client.on("error", (err) => {
        console.log(`[Redis Error - ${name}]`, err.message);
        connectionManager.setStatus(name, "disconnected");
    });

    client.on("ready", () => {
        connectionManager.setStatus(name, "connected");
    });

    client.on("reconnecting", () => {
        connectionManager.setStatus(name, "connecting");
    });

    client.on("end", () => {
        connectionManager.setStatus(name, "disconnected");
    });

    try {
        await client.connect();
    } catch (err) {
        console.log(`[Redis Connect Error - ${name}]`, err.message);
    }

    return createProxyClient(client, name);
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
