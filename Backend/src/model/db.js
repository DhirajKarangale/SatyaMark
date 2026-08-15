const { Pool } = require("pg");
require("dotenv").config();
const connectionManager = require("../utils/connectionManager");

const pool = new Pool({
    host: process.env.DB_HOST,
    port: Number(process.env.DB_PORT || 5432),
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,
    ssl: process.env.DB_SSL === "true"
        ? { rejectUnauthorized: false }
        : false,
    connectionTimeoutMillis: 10_000,
});

connectionManager.setStatus("postgres", "connecting");

pool.on("error", err => {
    console.log("PG Pool error:", err.message);
    connectionManager.setStatus("postgres", "disconnected");
});

async function checkPgHealth() {
    try {
        const client = await pool.connect();
        client.release();
        connectionManager.setStatus("postgres", "connected");
    } catch (err) {
        connectionManager.setStatus("postgres", "disconnected");
    }
}

setInterval(checkPgHealth, 5000);
checkPgHealth();

const wrappedPool = new Proxy(pool, {
    get(target, prop, receiver) {
        const originalMethod = target[prop];
        if (typeof originalMethod === 'function') {
            if (prop === 'query' || prop === 'connect') {
                return async function (...args) {
                    await connectionManager.ensureConnection("postgres");
                    return originalMethod.apply(target, args);
                };
            }
            return originalMethod.bind(target);
        }
        return Reflect.get(target, prop, receiver);
    }
});

module.exports = wrappedPool;
