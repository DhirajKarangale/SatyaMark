require("dotenv").config();

const express = require("express");
const bodyParser = require("body-parser");
const helmet = require("helmet");
const http = require("http");
const redis = require("redis");

const verifyRoutes = require("./routes/verify.routes");
const { wss, notifyUser } = require("./utils/ws-server");

const PORT = process.env.PORT;
const REDIS_URL = process.env.REDIS_URL;

const r = redis.createClient({ url: REDIS_URL });
r.connect().catch(err => {
    console.error("Redis connect error:", err);
});

const app = express();
app.use(helmet());
app.use(express.json());
app.use(bodyParser.json({ limit: "1mb" }));

app.use("/api/verify", verifyRoutes);

app.post("/ai-callback/text", async (req, res) => {
    try {
        const body = req.body;
        const { taskId, userId, job_token } = body;

        console.log("verifyPayload: ", body);

        if (!taskId || !userId || !job_token) {
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

        // console.log("verifyPayload: ", verifyPayload);

      

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