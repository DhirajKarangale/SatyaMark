const { Pool } = require("pg");
require("dotenv").config();

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

pool.on("error", err => {
    console.log("PG Pool error:", err.message);
});

module.exports = pool;
