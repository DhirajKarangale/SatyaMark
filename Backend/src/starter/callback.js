const express = require("express");
const bodyParser = require("body-parser");
const helmet = require("helmet");
const modelText = require('../model/modelText');
const modelImage = require('../model/modelImage');
const eventBus = require("../starter/eventBus"); 

const app = express();

app.use(helmet());
app.use(express.json());
app.use(bodyParser.json({ limit: "1mb" }));

app.post("/ai-callback/text", async (req, res) => {
    try {
        const body = req.body;
        await modelText.PostText(body);
        eventBus.emit("sendData", { clientId: body.clientId, payload: body });
        res.json({ ok: true });

    } catch (err) {
        console.error("Callback error:", err);
        res.status(500).json({ error: "server_error" });
    }
});

app.post("/ai-callback/image", async (req, res) => {
    try {
        
        const body = req.body;
        await modelImage.PostImage(body);
        eventBus.emit("sendData", { clientId: body.clientId, payload: body });
        res.json({ ok: true });

    } catch (err) {
        console.error("Callback error:", err);
        res.status(500).json({ error: "server_error" });
    }
});

module.exports = app;