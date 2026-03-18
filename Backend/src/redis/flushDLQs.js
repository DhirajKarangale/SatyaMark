require("dotenv").config();
const redis = require("redis");

const RENDER_TEXT_URL = process.env.REDIS_RENDER_TEXT_URL;
const UPSTASH_TEXT_URL = process.env.REDIS_UPSTASH_TEXT_URL;
const RENDER_IMAGE_URL = process.env.REDIS_RENDER_IMAGE_URL;
const UPSTASH_IMAGE_URL = process.env.REDIS_UPSTASH_IMAGE_URL;

const STREAM_KEY_TEXT = "stream:ai:text:jobs";
const STREAM_KEY_IMAGE = "stream:ai:image:jobs";

async function inspectAndClearDLQ(client, serverName, queueName, baseStreamKey) {
  const dlqStream = `${baseStreamKey}:dlq`;

  try {
    const messages = await client.xRange(dlqStream, '-', '+');

    if (!messages || messages.length === 0) {
      console.log(`[DLQ CLEANER] ${queueName} (${serverName}): DLQ is empty. Clean! ✨`);
      return;
    }

    console.log(`\n[DLQ CLEANER] Found ${messages.length} dead jobs in ${queueName} (${serverName}). Inspecting...`);

    for (const entry of messages) {
      const msgId = entry.id;
      const jobFields = entry.message;

      try {
        const payload = JSON.parse(jobFields.data);
        console.log(`\n --- DEAD LETTER JOB: ${payload.jobId} ---`);
        console.log(`Location:  ${queueName} Queue on ${serverName}`);
        console.log(`Retries:   ${payload.retry || 'Unknown'}`);
        console.log(`Payload:   `, payload);
        console.log(`-----------------------------------------`);
      } catch (parseErr) {
        console.log(`\n --- DEAD LETTER JOB: ${msgId} ---`);
        console.log(`Location:  ${queueName} Queue on ${serverName}`);
        console.log(`Raw Data:  `, jobFields.data);
        console.log(`-----------------------------------------`);
      }

      await client.xDel(dlqStream, msgId);
    }

    console.log(`[DLQ CLEANER] Successfully removed ${messages.length} jobs from ${dlqStream}.\n`);

  } catch (err) {
    console.log(`[DLQ CLEANER ERROR - ${queueName} ${serverName}] Failed to process DLQ:`, err.message);
  }
}

async function processDLQForQueue(renderUrl, upstashUrl, queueName, streamKey) {
  if (!renderUrl || !upstashUrl) return;

  const renderClient = redis.createClient({ url: renderUrl });
  const upstashClient = redis.createClient({ url: upstashUrl });

  renderClient.on("error", () => { });
  upstashClient.on("error", () => { });

  try {
    await renderClient.connect();
    await upstashClient.connect();

    await inspectAndClearDLQ(renderClient, "RENDER", queueName, streamKey);
    await inspectAndClearDLQ(upstashClient, "UPSTASH", queueName, streamKey);

  } catch (err) {
    console.log(`[CONNECTION ERROR - ${queueName}]`, err.message);
  } finally {
    if (renderClient.isOpen) await renderClient.quit();
    if (upstashClient.isOpen) await upstashClient.quit();
  }
}

async function flushAllDLQs() {
  console.log("Starting DLQ Inspection and Cleanup...");
  
  await Promise.all([
    processDLQForQueue(RENDER_TEXT_URL, UPSTASH_TEXT_URL, "TEXT", STREAM_KEY_TEXT),
    processDLQForQueue(RENDER_IMAGE_URL, UPSTASH_IMAGE_URL, "IMAGE", STREAM_KEY_IMAGE)
  ]);

  console.log("DLQ Cleanup Complete.");
  process.exit(0); 
}

flushAllDLQs();