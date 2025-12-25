const express = require("express");
const bodyParser = require("body-parser");
const helmet = require("helmet");
const cors = require("cors");
const modelText = require('../model/modelText');
const modelImage = require('../model/modelImage');
const eventBus = require("../starter/eventBus");

const app = express();

app.use(cors());
app.use(helmet());
app.use(express.json());
app.use(bodyParser.json({ limit: "1mb" }));

app.get('/health', async (req, res, next) => {
    try {
        res.status(200).json("Ok");
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
            summary: savedData.summary,
            type: "text",
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
            image_url: savedData.image_url,
            type: "image",
        };

        eventBus.emit("sendData", { clientId: body.clientId, payload: payload });
        res.json({ ok: true });

    } catch (err) {
        console.error("Callback error:", err);
        res.status(500).json({ error: "server_error" });
    }
});

module.exports = app;