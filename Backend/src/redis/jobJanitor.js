require("dotenv").config();
const { getClients } = require("./redisClient");

const JANITOR_RATE_MS = parseInt(process.env.REDIS_RENDER_UPSTASH_TRANSFER_RATE) || 60000;

const STREAM_KEY_TEXT = "stream:ai:text:jobs";
const STREAM_KEY_IMAGE = "stream:ai:image:jobs";
const GROUP_NAME = "workers";
const JANITOR_NAME = "backend-janitor";
const IDLE_TIME_MS = 10 * 60 * 1000; // 10 minutes
const MAX_RETRY = 3;

async function cleanStuckJobs(client, serverName, queueName, streamKey) {
  if (!client) return;
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

async function runJanitorCycle() {
  const { renderText, upstashText, renderImage, upstashImage } = getClients();

  await Promise.all([
    cleanStuckJobs(renderText, "RENDER", "TEXT", STREAM_KEY_TEXT),
    cleanStuckJobs(upstashText, "UPSTASH", "TEXT", STREAM_KEY_TEXT),
    cleanStuckJobs(renderImage, "RENDER", "IMAGE", STREAM_KEY_IMAGE),
    cleanStuckJobs(upstashImage, "UPSTASH", "IMAGE", STREAM_KEY_IMAGE)
  ]);
}

function startJanitorCycle() {
  setInterval(runJanitorCycle, JANITOR_RATE_MS);
}

module.exports = { startJanitorCycle };
