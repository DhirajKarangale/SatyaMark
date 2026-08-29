const express = require("express");
const bodyParser = require("body-parser");
const helmet = require("helmet");
const cors = require("cors");
const modelText = require('../model/modelText');
const modelImage = require('../model/modelImage');
const redisEventBus = require("./redisEventBus");
const messages = require("../utils/messages.json");

const app = express();

app.use(cors());
app.use(helmet());
app.use(express.json());
app.use(bodyParser.json({ limit: "1mb" }));

app.get('/', (req, res) => {
    const randomMessage = messages.root[Math.floor(Math.random() * messages.root.length)];
    res.status(200).json({ message: randomMessage });
});

app.get('/health', async (req, res, next) => {
    try {
        const randomMessage = messages.health[Math.floor(Math.random() * messages.health.length)];
        res.status(200).json({ message: randomMessage });
    } catch (error) {
        next(error);
    }
});

app.get("/getTextResult", async (req, res) => {
    const id = req.query.id;
    const textData = await modelText.GetTextById(id);
    res.json({
        ...textData,
        type: "text",
    });
});

app.get("/getImageResult", async (req, res) => {
    const id = req.query.id;
    const imageData = await modelImage.GetImageById(id);
    res.json({
        ...imageData,
        type: "image",
    });
});

app.post("/text/remove", async (req, res) => {

    try {
        const { id } = req.body;
        if (!id) {
            return res.status(400).json({
                success: false,
                message: "Text id is required"
            });
        }

        const deleted = await modelText.DeleteTextById(id);

        if (!deleted) {
            return res.status(404).json({
                success: false,
                message: "Text not found"
            });
        }

        return res.status(200).json({
            success: true,
            message: "Successful"
        });
    } catch (error) {
        return res.status(500).json({
            success: false,
            message: "Error occurred while performing operation"
        });
    }
});

app.post("/image/remove", async (req, res) => {
    try {
        const { id } = req.body;

        if (!id) {
            return res.status(400).json({
                success: false,
                message: "Image id is required"
            });
        }

        const deleted = await modelImage.DeleteImageById(id);

        if (!deleted) {
            return res.status(404).json({
                success: false,
                message: "Image not found"
            });
        }

        return res.status(200).json({
            success: true,
            message: "Successful"
        });
    } catch (error) {
        return res.status(500).json({
            success: false,
            message: "Error occurred while performing operation"
        });
    }
});

app.post("/ai-callback/text", async (req, res) => {
    try {
        const body = req.body;

        const { jobId, clientId, mark, reason, confidence, summary, urls } = body;
        console.log(`[TEXT] Callback received → client=${clientId}, job=${jobId}`);

        const reasonText = (reason || "").toLowerCase();

        const isInternalError = mark === "ERROR" || reasonText.includes("internal error occurred") ||
            reasonText.includes("failed to generate") ||
            reasonText.includes("models and tokens failed") ||
            reasonText.includes("pipeline execution failed");

        let dbId = null;
        if (!isInternalError) {
            try {
                // Fix #13: Recompute summary_hash using the AI's normalized summary output
                const { generateTextHashes } = require("../hash/text_hash");
                if (body.summary) {
                    body.summary_hash = generateTextHashes(body.summary).summary_hash;
                }
                const dbResult = await modelText.PostText(body);
                dbId = dbResult?.id;
            } catch (dbErr) {
                console.log("[TEXT] DB Insert Error:", dbErr.message);
            }
        }

        const payload = {
            jobId: jobId,
            clientId: clientId,
            mark: mark,
            confidence: confidence,
            reason: reason,
            urls: urls,
            summary: summary,
            type: "text",
            dataId: dbId,
        };

        await redisEventBus.publishData({ clientId: body.clientId, payload: payload });
        res.json({ ok: true });

    } catch (err) {
        console.log("Callback error:", err);
        res.status(500).json({ error: "server_error" });
    }
});

app.post("/ai-callback/image", async (req, res) => {
    try {
        const body = req.body;
        const { jobId, clientId, image_hash, image_url, mark, reason, confidence } = body;

        console.log(`[IMAGE] Callback received → client=${clientId}, job=${jobId}`);

        const reasonText = (reason || "").toLowerCase();

        const isInternalError = mark === "ERROR" || reasonText.includes("internal error occurred") ||
            reasonText.includes("failed to generate") ||
            reasonText.includes("models and tokens failed") ||
            reasonText.includes("pipeline execution failed");

        let dbId = null;
        if (!isInternalError) {
            try {
                const dbResult = await modelImage.PostImage(body);
                dbId = dbResult?.id;
            } catch (dbErr) {
                console.log("[IMAGE] DB Insert Error:", dbErr.message);
            }
        }

        const payload = {
            jobId: jobId,
            clientId: clientId,
            mark: mark,
            confidence: confidence,
            reason: reason,
            image_url: image_url,
            type: "image",
            dataId: dbId,
        };

        await redisEventBus.publishData({ clientId: body.clientId, payload: payload });
        res.json({ ok: true });

    } catch (err) {
        console.log("Callback error:", err);
        res.status(500).json({ error: "server_error" });
    }
});

module.exports = app;