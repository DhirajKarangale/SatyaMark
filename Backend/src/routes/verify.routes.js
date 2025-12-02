const express = require("express");
const router = express.Router();
const { generateTextHashes } = require('../hash/text_hash');
const { enqueueJob } = require("../utils/enqueueJob");
const modelHash = require('../model/modelHash');

const callback_url_text = process.env.RESULT_RECEIVER_TEXT;

router.post("/text", async (req, res) => {
  try {
    const { text } = req.body;

    if (!text) return res.status(400).json({ error: "text missing" });

    const { originalHash, summaryHash } = generateTextHashes(text)
    const textData = await modelHash.GetText(originalHash, summaryHash);
    if (textData) return res.json(textData);

    const { taskId } = await enqueueJob({
      payload: { text },
      callback_url: callback_url_text,
    });

    res.json({ queued: true, taskId });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "failed_to_enqueue" });
  }
});

router.post("/img-ml", async (req, res) => {
  try {
    const userId = req.user.userId;
    const { url } = req.body;

    if (!url) return res.status(400).json({ error: "url missing" });

    const callback_url = process.env.RESULT_RECEIVER_IMG;

    const { taskId } = await enqueueJob({
      userId,
      payload: { url },
      callback_url,
    });

    res.json({ queued: true, taskId });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "failed_to_enqueue" });
  }
});

router.post("/img-forensic", async (req, res) => {
  try {
    const userId = req.user.userId;
    const { url } = req.body;

    if (!url) return res.status(400).json({ error: "url missing" });

    const callback_url = process.env.RESULT_RECEIVER_URL;

    const { taskId } = await enqueueJob({
      userId,
      payload: { url },
      callback_url,
    });

    res.json({ queued: true, taskId });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "failed_to_enqueue" });
  }
});

module.exports = router;