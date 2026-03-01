const redis = require("redis");
require("dotenv").config();

// 1. The In-Memory Job Queue
const localJobQueue = [];
let isProcessing = false;

// Helper: Get actual RAM usage of Render in Megabytes
async function getRenderMemoryMB(client) {
  try {
    const memoryInfo = await client.info('memory');
    const match = memoryInfo.match(/used_memory:(\d+)/);
    if (match) {
      const bytes = parseInt(match[1], 10);
      return bytes / (1024 * 1024); // Convert to MB
    }
  } catch (err) {
    console.error("[MEMORY CHECK ERROR]", err.message);
  }
  return 0;
}

// 2. Put the job object in the local queue instantly (No returns needed)
async function enqueueJob(jobData) {
  if (!jobData.STREAM_KEY) {
    console.log("STREAM_KEY is undefined");
    return;
  }

  localJobQueue.push(jobData);
  console.log(`[QUEUE] Job ${jobData.jobId} added to memory queue. (Queue size: ${localJobQueue.length})`);
}

// 3. The Queue Processor (Runs every 5 seconds)
async function processQueue() {
  if (isProcessing || localJobQueue.length === 0) return;

  isProcessing = true;

  // Define clients locally so they only exist during this cycle
  let renderClient = null;
  let upstashClient = null;

  try {
    // Always connect to Render first to check memory
    renderClient = redis.createClient({ url: process.env.REDIS_RENDER_TEXT_URL });
    renderClient.on("error", (e) => console.log("[RENDER ROUTER ERROR]", e.message));
    await renderClient.connect();

    // Check the RAM usage once per cycle
    let usedMB = await getRenderMemoryMB(renderClient);

    while (localJobQueue.length > 0) {
      const currentJob = localJobQueue[0];
      const streamKey = currentJob.STREAM_KEY;
      const jobPayload = { data: JSON.stringify(currentJob) };

      if (usedMB < 22) {
        // Render has physical RAM space -> Add it there
        await renderClient.xAdd(streamKey, "*", jobPayload);
        console.log(`[ROUTER] Job ${currentJob.jobId} routed to RENDER (${usedMB.toFixed(2)} MB / 25 MB used).`);
      } else {
        // Render RAM is dangerously close to 25MB -> Route to Upstash
        // Only connect to Upstash if we actually need to use it
        if (!upstashClient) {
          upstashClient = redis.createClient({ url: process.env.REDIS_UPSTASH_TEXT_URL });
          upstashClient.on("error", (e) => console.log("[UPSTASH ROUTER ERROR]", e.message));
          await upstashClient.connect();
        }

        await upstashClient.xAdd(streamKey, "*", jobPayload);
        console.log(`[ROUTER] Render RAM Full (${usedMB.toFixed(2)} MB). Job ${currentJob.jobId} routed to UPSTASH.`);
      }

      // Successfully added to a DB, remove from local queue
      localJobQueue.shift();
    }

  } catch (error) {
    console.error("[QUEUE PROCESSOR ERROR]", error.message);
  } finally {
    // 4. Manually close connections at the very end
    try {
      if (renderClient && renderClient.isOpen) {
        await renderClient.quit();
      }
      if (upstashClient && upstashClient.isOpen) {
        await upstashClient.quit();
      }
    } catch (closeErr) {
      console.error("[ROUTER CLOSE ERROR]", closeErr.message);
    }

    isProcessing = false;
  }
}

// Start the 5-second interval
setInterval(processQueue, 5000);

module.exports = { enqueueJob };