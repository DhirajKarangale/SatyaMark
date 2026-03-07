require("dotenv").config();
const redis = require("redis");

const RENDER_URL = process.env.REDIS_RENDER_TEXT_URL;
const UPSTASH_URL = process.env.REDIS_UPSTASH_TEXT_URL;
const TRANSFER_RATE_MS = parseInt(process.env.REDIS_RENDER_UPSTASH_TRANSFER_RATE);

const STREAM_KEY = "stream:ai:text:jobs";
const GROUP_NAME = "workers";
const CONSUMER_NAME = "transfer-node-script"; // Unique name for the backend script

let isTransferring = false;

async function transferJobs() {
  if (isTransferring) return;
  isTransferring = true;

  const renderClient = redis.createClient({ url: RENDER_URL });
  const upstashClient = redis.createClient({ url: UPSTASH_URL });

  renderClient.on("error", (e) => console.log("[RENDER ERROR]", e.message));
  upstashClient.on("error", (e) => console.log("[UPSTASH ERROR]", e.message));

  try {
    await renderClient.connect();
    await upstashClient.connect();

    const response = await renderClient.xReadGroup(
      GROUP_NAME,
      CONSUMER_NAME,
      [{ key: STREAM_KEY, id: ">" }],
      { COUNT: 500 } 
    );

    if (!response || response.length === 0) {
      console.log(`[TRANSFER] No unassigned jobs in Render. Sleeping.`);
      return;
    }

    const messages = response[0].messages;
    console.log(`[TRANSFER] Scooped ${messages.length} unassigned jobs. Moving to Upstash...`);
    
    let successCount = 0;

    for (const entry of messages) {
      const renderMessageId = entry.id;
      const jobData = entry.message;

      try {
        await upstashClient.xAdd(STREAM_KEY, "*", jobData);
        await renderClient.xAck(STREAM_KEY, GROUP_NAME, renderMessageId);
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