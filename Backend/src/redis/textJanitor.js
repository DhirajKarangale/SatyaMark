require("dotenv").config();
const redis = require("redis");

const RENDER_URL = process.env.REDIS_RENDER_TEXT_URL;
const UPSTASH_URL = process.env.REDIS_UPSTASH_TEXT_URL;
const JANITOR_RATE_MS = parseInt(process.env.REDIS_RENDER_UPSTASH_TRANSFER_RATE);

const STREAM_KEY = "stream:ai:text:jobs";
const GROUP_NAME = "workers";
const JANITOR_NAME = "backend-janitor";
const IDLE_TIME_MS = 10 * 60 * 1000;

async function cleanStuckJobs(client, clientName) {
  try {
    const response = await client.xAutoClaim(
      STREAM_KEY,
      GROUP_NAME,
      JANITOR_NAME,
      IDLE_TIME_MS,
      "0-0", 
      { COUNT: 100 } 
    );

    const messages = response.messages;

    if (!messages || messages.length === 0) {
      return;
    }

    console.log(`[JANITOR] Found ${messages.length} stuck jobs in ${clientName}. Re-queueing...`);

    for (const entry of messages) {
      const stuckMsgId = entry.id;
      const jobData = entry.message;

      try {
        await client.xAdd(STREAM_KEY, "*", jobData);
        await client.xAck(STREAM_KEY, GROUP_NAME, stuckMsgId);
        await client.xDel(STREAM_KEY, stuckMsgId);

      } catch (err) {
        console.log(`[JANITOR ERROR] Failed to reset job ${stuckMsgId}:`, err.message);
      }
    }
  } catch (err) {
    if (!err.message.includes("NOGROUP")) {
      console.log(`[JANITOR SYSTEM ERROR - ${clientName}]`, err.message);
    }
  }
}

async function runJanitorCycle() {
  const renderClient = redis.createClient({ url: RENDER_URL });
  const upstashClient = redis.createClient({ url: UPSTASH_URL });

  renderClient.on("error", () => { });
  upstashClient.on("error", () => { });

  try {
    await renderClient.connect();
    await upstashClient.connect();

    await cleanStuckJobs(renderClient, "RENDER");
    await cleanStuckJobs(upstashClient, "UPSTASH");

  } catch (err) {
    console.log("[JANITOR CONNECTION ERROR]", err.message);
  } finally {
    if (renderClient.isOpen) await renderClient.quit();
    if (upstashClient.isOpen) await upstashClient.quit();
  }
}

function startJanitorCycle() {
  setInterval(runJanitorCycle, JANITOR_RATE_MS);
}

module.exports = { startJanitorCycle };