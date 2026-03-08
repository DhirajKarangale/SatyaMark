require("dotenv").config();
const redis = require("redis");

const RENDER_URL = process.env.REDIS_RENDER_TEXT_URL;
const UPSTASH_URL = process.env.REDIS_UPSTASH_TEXT_URL;

async function scanDatabases() {
  console.log("🔍 Scanning databases for keys...\n");

  const renderClient = redis.createClient({ url: RENDER_URL });
  const upstashClient = redis.createClient({ url: UPSTASH_URL });

  renderClient.on("error", () => {});
  upstashClient.on("error", () => {});

  try {
    await renderClient.connect();
    await upstashClient.connect();

    // Scan Render
    console.log("--- RENDER REDIS ---");
    const renderKeys = await renderClient.keys("*");
    if (renderKeys.length === 0) {
      console.log("No keys found. Database is empty.");
    } else {
      for (const key of renderKeys) {
        const type = await renderClient.type(key);
        console.log(`🔑 Key: '${key}' | Type: [${type}]`);
      }
    }

    console.log("\n--- UPSTASH REDIS ---");
    // Scan Upstash
    const upstashKeys = await upstashClient.keys("*");
    if (upstashKeys.length === 0) {
      console.log("No keys found. Database is empty.");
    } else {
      for (const key of upstashKeys) {
        const type = await upstashClient.type(key);
        console.log(`🔑 Key: '${key}' | Type: [${type}]`);
      }
    }

    console.log("\nScan complete.");

  } catch (error) {
    console.error("Failed to scan databases:", error.message);
  } finally {
    if (renderClient.isOpen) await renderClient.quit();
    if (upstashClient.isOpen) await upstashClient.quit();
    process.exit(0);
  }
}

scanDatabases();