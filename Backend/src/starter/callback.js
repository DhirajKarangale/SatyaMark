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

app.get("/getResult", async (req, res) => {
    const id = req.params.id;

    const textData = await modelText.GetTextById(id);
    if (textData) {
        res.json(textData);
        return;
    }

    const imageData = await modelImage.GetImageById(id);

    if (imageData) {
        res.json(imageData);
        return;
    }

    res.json("No Data found");
});

app.post("/ai-callback/text", async (req, res) => {
    try {
        const body = req.body;
        console.log(`[TEXT] Callback received → client=${body.clientId}, job=${body.jobId}`);
        const savedData = await modelText.PostText(body);

        const payload = {
            jobId: body.jobId,
            clientId: body.clientId,
            dataId: savedData.id,
            mark: savedData.mark,
            confidence: savedData.confidence,
            reason: savedData.reason,
            urls: savedData.urls,
        };

        eventBus.emit("sendData", { clientId: body.clientId, payload: payload });
        res.json({ ok: true });

    } catch (err) {
        console.error("Callback error:", err);
        res.status(500).json({ error: "server_error" });
    }
});

app.post("/ai-callback/image", async (req, res) => {
    try {
        const body = req.body;
        console.log(`[IMAGE] Callback received → client=${body.clientId}, job=${body.jobId}`);
        const savedData = await modelImage.PostImage(body);

        const payload = {
            jobId: body.jobId,
            clientId: body.clientId,
            dataId: savedData.id,
            mark: savedData.mark,
            confidence: savedData.confidence,
            reason: savedData.reason,
        };

        eventBus.emit("sendData", { clientId: body.clientId, payload: payload });
        res.json({ ok: true });

    } catch (err) {
        console.error("Callback error:", err);
        res.status(500).json({ error: "server_error" });
    }
});

module.exports = app;