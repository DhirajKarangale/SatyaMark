require("dotenv").config();
const redis = require("redis");

const RENDER_TEXT_URL = process.env.REDIS_RENDER_TEXT_URL;
const UPSTASH_TEXT_URL = process.env.REDIS_UPSTASH_TEXT_URL;
const RENDER_IMAGE_URL = process.env.REDIS_RENDER_IMAGE_URL;
const UPSTASH_IMAGE_URL = process.env.REDIS_UPSTASH_IMAGE_URL;

const STREAM_KEY_TEXT = "stream:ai:text:jobs";
const STREAM_KEY_IMAGE = "stream:ai:image:jobs";

async function logKeys(client, name) {
  console.log(`${name} Keys:`);
  let cursor = "0";
  let total = 0;

  do {
    const reply = await client.scan(cursor, { MATCH: "*", COUNT: 100 });
    cursor = reply.cursor;
    const keys = reply.keys;

    for (const key of keys) {
      const type = await client.type(key);
      console.log(`${key} (${type})`);
      total++;
    }
  } while (cursor !== "0");

  if (total === 0) console.log("None.");
}

async function clearDatabases() {
  const renderClient = redis.createClient({ url: RENDER_IMAGE_URL });
  const upstashClient = redis.createClient({ url: UPSTASH_IMAGE_URL });

  renderClient.on("error", () => { });
  upstashClient.on("error", () => { });

  try {
    await renderClient.connect();
    await upstashClient.connect();

    await logKeys(renderClient, "RENDER");
    await logKeys(upstashClient, "UPSTASH");

    console.log("Deleting keys...");
    await renderClient.flushDb();
    await upstashClient.flushDb();
    console.log("Done.");
  } catch (err) {
    console.error("Error:", err.message);
  } finally {
    if (renderClient.isOpen) await renderClient.quit();
    if (upstashClient.isOpen) await upstashClient.quit();
  }
}

async function inspectAndClearDLQ(client, serverName, queueName, baseStreamKey) {
  const dlqStream = `${baseStreamKey}:dlq`;

  try {
    const messages = await client.xRange(dlqStream, '-', '+');

    if (!messages || messages.length === 0) {
      console.log(`${queueName} (${serverName}) DLQ: Empty`);
      return;
    }

    console.log(`${queueName} (${serverName}) DLQ: Found ${messages.length} jobs`);

    for (const entry of messages) {
      const msgId = entry.id;
      const jobFields = entry.message;

      try {
        const payload = JSON.parse(jobFields.data);
        console.log(`Job ${payload.jobId}:`, payload);
      } catch (parseErr) {
        console.log(`Job ${msgId}:`, jobFields.data);
      }

      await client.xDel(dlqStream, msgId);
    }

    console.log(`Removed ${messages.length} jobs from ${dlqStream}`);
  } catch (err) {
    console.log(`Error ${queueName} ${serverName}:`, err.message);
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
    console.log(`Error ${queueName}:`, err.message);
  } finally {
    if (renderClient.isOpen) await renderClient.quit();
    if (upstashClient.isOpen) await upstashClient.quit();
  }
}

async function flushAllDLQs() {
  console.log("Checking DLQs...");

  await Promise.all([
    processDLQForQueue(RENDER_TEXT_URL, UPSTASH_TEXT_URL, "TEXT", STREAM_KEY_TEXT),
    processDLQForQueue(RENDER_IMAGE_URL, UPSTASH_IMAGE_URL, "IMAGE", STREAM_KEY_IMAGE)
  ]);

  console.log("Done.");
}

async function wipeAllRedisData() {
  console.log("Clearing all Redis data...");
  const urls = [
    { name: "RENDER_TEXT", url: RENDER_TEXT_URL },
    { name: "UPSTASH_TEXT", url: UPSTASH_TEXT_URL },
    { name: "RENDER_IMAGE", url: RENDER_IMAGE_URL },
    { name: "UPSTASH_IMAGE", url: UPSTASH_IMAGE_URL },
  ];

  for (const { name, url } of urls) {
    if (!url) continue;
    const client = redis.createClient({ url });
    client.on("error", () => { });

    try {
      await client.connect();
      console.log(`Flushing ${name}...`);
      await client.flushAll();
      console.log(`${name} cleared.`);
    } catch (err) {
      console.log(`Error ${name}:`, err.message);
    } finally {
      if (client.isOpen) await client.quit();
    }
  }
  console.log("Done.");
}

async function main() {
  // await clearDatabases();
  // await flushAllDLQs();
  await wipeAllRedisData();

  process.exit(0);
}

main();
