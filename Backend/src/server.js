require("dotenv").config();

const express = require("express");
const bodyParser = require("body-parser");
const helmet = require("helmet");
const crypto = require("crypto");
const http = require("http");
const { Client } = require("pg");
const redis = require("redis");

const verifyRoutes = require("./routes/verify.routes");
const { wss, notifyUser } = require("./utils/ws-server");

const PORT = process.env.PORT;
const DATABASE_URL = process.env.DATABASE_URL;
const REDIS_URL = process.env.REDIS_URL;

const pg = new Client({ connectionString: DATABASE_URL });
pg.connect().catch(err => {
    console.error("Postgres connect error:", err);
    process.exit(1);
});

const r = redis.createClient({ url: REDIS_URL });
r.connect().catch(err => {
    console.error("Redis connect error:", err);
});

const app = express();
app.use(helmet());
app.use(express.json());
app.use(bodyParser.json({ limit: "1mb" }));

app.use("/api/verify", verifyRoutes);

app.post("/ai-callback", async (req, res) => {
    try {
        const body = req.body;
        const { taskId, userId, job_token, hmac: providedHmac } = body;

        if (!taskId || !userId || !job_token || !providedHmac) {
            return res.status(400).json({ error: "missing fields" });
        }

        const verifyPayload = {
            taskId,
            userId,
            job_token,
            mark: body.mark,
            reason: body.reason,
            confidence: body.confidence,
        };

        console.log("verifyPayload: ", verifyPayload);

        // await pg.query(
        //     `INSERT INTO ai_results 
        //     (id, user_id, text_hash, summary_hash, mark, reason, confidence, job_token)
        //     VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
        //     ON CONFLICT (id) DO UPDATE 
        //     SET mark=$5, reason=$6, confidence=$7, job_token=$8, received_at=NOW()`,
        //     [
        //         taskId,
        //         userId,
        //         body.text_hash || null,
        //         body.summary_hash || null,
        //         body.mark,
        //         body.reason,
        //         body.confidence,
        //         job_token
        //     ]
        // );

        // notifyUser(userId, {
        //     type: "ai_result",
        //     data: body,
        // });

        return res.json({ ok: true });
    } catch (err) {
        console.error("ai-callback error:", err);
        res.status(500).json({ error: "server_error" });
    }
});

app.get("/", (req, res) => res.json({ service: "Unified Backend Running" }));

const server = http.createServer(app);

server.on("upgrade", (req, socket, head) => {
    const url = new URL(req.url, `http://${req.headers.host}`);
    const token = url.searchParams.get("token");

    wss.handleUpgrade(req, socket, head, (ws) => {
        wss.emit("connection", ws, req, token);
    });
});

server.listen(PORT, () => {
    console.log(`Unified Backend + Result Receiver running on port ${PORT}`);
});