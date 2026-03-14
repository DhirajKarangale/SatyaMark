require("dotenv").config();
const redis = require("redis");

const RENDER_URL = process.env.REDIS_RENDER_IMAGE_URL;
const UPSTASH_URL = process.env.REDIS_UPSTASH_IMAGE_URL;

async function logKeys(client, name) {
  console.log(`\n--- ${name} REDIS KEYS ---`);

  let cursor = "0";
  let total = 0;

  do {
    const reply = await client.scan(cursor, { MATCH: "*", COUNT: 100 });
    cursor = reply.cursor;
    const keys = reply.keys;

    for (const key of keys) {
      const type = await client.type(key);
      console.log(`🔑 ${key} | Type: ${type}`);
      total++;
    }

  } while (cursor !== "0");

  if (total === 0) console.log("No keys found.");
}

async function clearDatabases() {
  const renderClient = redis.createClient({ url: RENDER_URL });
  const upstashClient = redis.createClient({ url: UPSTASH_URL });

  renderClient.on("error", () => {});
  upstashClient.on("error", () => {});

  try {
    await renderClient.connect();
    await upstashClient.connect();

    await logKeys(renderClient, "RENDER");
    await logKeys(upstashClient, "UPSTASH");

    console.log("\nDeleting all keys...");

    await renderClient.flushDb();
    await upstashClient.flushDb();

    console.log("All Redis data deleted.");

  } catch (err) {
    console.error("Error:", err.message);
  } finally {
    if (renderClient.isOpen) await renderClient.quit();
    if (upstashClient.isOpen) await upstashClient.quit();
    process.exit(0);
  }
}

clearDatabases();