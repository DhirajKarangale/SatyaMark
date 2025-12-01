const express = require("express");
const router = express.Router();
const { enqueueJob } = require("../utils/enqueueJob");

// TEXT
router.post("/text", async (req, res) => {
  try {
    // const userId = req.user.userId; // coming from JWT middleware
    const userId = req.body.userId; // coming from JWT middleware
    const { text } = req.body;

    if (!text) return res.status(400).json({ error: "text missing" });

    const callback_url = process.env.RESULT_RECEIVER_URL;

    const { taskId } = await enqueueJob({
      userId,
      payload: { text },
      callback_url,
    });

    res.json({ queued: true, taskId });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "failed_to_enqueue" });
  }
});

// IMAGE ML
router.post("/img-ml", async (req, res) => {
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

// IMAGE FORENSIC
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
