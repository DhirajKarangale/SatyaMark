require("dotenv").config();
const redis = require("redis");

const RENDER_TEXT_URL = process.env.REDIS_RENDER_TEXT_URL;
const UPSTASH_TEXT_URL = process.env.REDIS_UPSTASH_TEXT_URL;
const RENDER_IMAGE_URL = process.env.REDIS_RENDER_IMAGE_URL;
const UPSTASH_IMAGE_URL = process.env.REDIS_UPSTASH_IMAGE_URL;

const JANITOR_RATE_MS = parseInt(process.env.REDIS_RENDER_UPSTASH_TRANSFER_RATE) || 60000;

const STREAM_KEY_TEXT = "stream:ai:text:jobs";
const STREAM_KEY_IMAGE = "stream:ai:image:jobs";
const GROUP_NAME = "workers";
const JANITOR_NAME = "backend-janitor";
const IDLE_TIME_MS = 10 * 60 * 1000; // 10 minutes
const MAX_RETRY = 3;

async function cleanStuckJobs(client, serverName, queueName, streamKey) {
  try {
    const response = await client.xAutoClaim(
      streamKey,
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

    console.log(`[JANITOR] Found ${messages.length} stuck jobs in ${queueName} (${serverName}). Checking retries...`);

    for (const entry of messages) {
      const stuckMsgId = entry.id;
      const jobFields = entry.message;

      try {
        const payloadStr = jobFields.data;
        const payload = JSON.parse(payloadStr);

        payload.retry = (payload.retry || 0) + 1;

        if (payload.retry > MAX_RETRY) {
          console.log(`[DLQ] Job ${payload.jobId} failed 3 times in ${queueName}. Moving to DLQ.`);

          const dlqStream = `${streamKey}:dlq`;
          await client.xAdd(dlqStream, "*", { data: JSON.stringify(payload) });

          await client.xAck(streamKey, GROUP_NAME, stuckMsgId);
          await client.xDel(streamKey, stuckMsgId);
          continue;
        }

        jobFields.data = JSON.stringify(payload);

        await client.xAdd(streamKey, "*", jobFields);
        await client.xAck(streamKey, GROUP_NAME, stuckMsgId);
        await client.xDel(streamKey, stuckMsgId);

      } catch (err) {
        console.log(`[JANITOR ERROR] Failed to reset job ${stuckMsgId} in ${queueName}:`, err.message);
      }
    }
  } catch (err) {
    if (!err.message.includes("NOGROUP")) {
      console.log(`[JANITOR SYSTEM ERROR - ${queueName} ${serverName}]`, err.message);
    }
  }
}

async function processJanitorForQueue(renderUrl, upstashUrl, queueName, streamKey) {
  if (!renderUrl || !upstashUrl) return;

  const renderClient = redis.createClient({ url: renderUrl });
  const upstashClient = redis.createClient({ url: upstashUrl });

  renderClient.on("error", () => { });
  upstashClient.on("error", () => { });

  try {
    await renderClient.connect();
    await upstashClient.connect();

    await cleanStuckJobs(renderClient, "RENDER", queueName, streamKey);
    await cleanStuckJobs(upstashClient, "UPSTASH", queueName, streamKey);

  } catch (err) {
    console.log(`[JANITOR CONNECTION ERROR - ${queueName}]`, err.message);
  } finally {
    if (renderClient.isOpen) await renderClient.quit();
    if (upstashClient.isOpen) await upstashClient.quit();
  }
}

async function runJanitorCycle() {
  await Promise.all([
    processJanitorForQueue(RENDER_TEXT_URL, UPSTASH_TEXT_URL, "TEXT", STREAM_KEY_TEXT),
    processJanitorForQueue(RENDER_IMAGE_URL, UPSTASH_IMAGE_URL, "IMAGE", STREAM_KEY_IMAGE)
  ]);
}

function startJanitorCycle() {
  setInterval(runJanitorCycle, JANITOR_RATE_MS);
}

module.exports = { startJanitorCycle };