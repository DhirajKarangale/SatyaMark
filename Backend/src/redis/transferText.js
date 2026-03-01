require("dotenv").config();
const redis = require("redis");

const RENDER_URL = process.env.REDIS_RENDER_TEXT_URL;
const UPSTASH_URL = process.env.REDIS_UPSTASH_TEXT_URL;
const TRANSFER_RATE_MS = parseInt(process.env.REDIS_RENDER_UPSTASH_TRANSFER_RATE) * 1000;

const STREAM_KEY = "stream:ai:text:jobs";

let isTransferring = false;

async function transferJobs() {
  if (isTransferring) {
    console.log("[TRANSFER] Previous transfer still running, skipping this cycle.");
    return;
  }

  isTransferring = true;
  console.log(`\n[TRANSFER] Waking up to check Render stream...`);

  const renderClient = redis.createClient({ url: RENDER_URL });
  const upstashClient = redis.createClient({ url: UPSTASH_URL });

  renderClient.on("error", (e) => console.log("[RENDER ERROR]", e.message));
  upstashClient.on("error", (e) => console.log("[UPSTASH ERROR]", e.message));

  try {
    await renderClient.connect();
    await upstashClient.connect();

    const messages = await renderClient.xRange(STREAM_KEY, '-', '+');

    if (!messages || messages.length === 0) {
      console.log(`[TRANSFER] Render stream is empty. Going back to sleep.`);
      return; 
    }

    console.log(`[TRANSFER] Found ${messages.length} jobs. Starting transfer...`);
    let successCount = 0;

    for (const entry of messages) {
      const renderMessageId = entry.id;
      const jobData = entry.message;

      try {
        await upstashClient.xAdd(STREAM_KEY, "*", jobData);
        await renderClient.xDel(STREAM_KEY, renderMessageId);

        successCount++;
      } catch (err) {
        console.log(`[TRANSFER ERROR] Failed to move job ID ${renderMessageId}:`, err.message);
      }
    }

    console.log(`[TRANSFER] Successfully moved ${successCount}/${messages.length} jobs to Upstash.`);

  } catch (error) {
    console.log("[TRANSFER SYSTEM ERROR]", error.message);
  } finally {
    try {
      if (renderClient.isOpen) await renderClient.quit();
      if (upstashClient.isOpen) await upstashClient.quit();
      console.log(`[TRANSFER] Connections gracefully closed.`);
    } catch (closeErr) {
      console.log("[TRANSFER CLOSE ERROR]", closeErr.message);
    }

    isTransferring = false;
  }
}

function startTextTransfer() {
  setInterval(transferJobs, TRANSFER_RATE_MS);
}

module.exports = { startTextTransfer };