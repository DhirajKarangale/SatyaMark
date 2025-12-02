const express = require("express");
const bodyParser = require("body-parser");
const helmet = require("helmet");

const { sendToUser } = require("./ws-server");

const app = express();

app.use(helmet());
app.use(express.json());
app.use(bodyParser.json({ limit: "1mb" }));

app.post("/ai-callback/text", async (req, res) => {
    try {
        const body = req.body;
        console.log("Callback received:", body);
        res.json({ ok: true });

    } catch (err) {
        console.error("Callback error:", err);
        res.status(500).json({ error: "server_error" });
    }
});

module.exports = app;