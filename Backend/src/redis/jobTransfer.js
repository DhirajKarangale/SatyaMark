require("dotenv").config();
const { getClients } = require("./redisClient");

const TRANSFER_RATE_MS = parseInt(process.env.REDIS_RENDER_UPSTASH_TRANSFER_RATE) || 60000;

const GROUP_NAME = "workers";
const CONSUMER_NAME = "transfer-node-script";

let isTransferring = false;

async function transferQueue(renderClient, upstashClient, streamKey, queueName) {
    if (!renderClient || !upstashClient) return;

    try {
        const response = await renderClient.xReadGroup(
            GROUP_NAME,
            CONSUMER_NAME,
            [{ key: streamKey, id: "0" }],
            { COUNT: 500 }
        );

        if (!response || response.length === 0) {
            return;
        }

        const messages = response[0].messages;
        console.log(`[TRANSFER] Scooped ${messages.length} unassigned jobs from ${queueName}. Moving to Upstash...`);
        
        let successCount = 0;

        for (const entry of messages) {
            const renderMessageId = entry.id;
            const jobData = entry.message;

            try {
                await upstashClient.xAdd(streamKey, "*", jobData);
                await renderClient.xAck(streamKey, GROUP_NAME, renderMessageId);
                await renderClient.xDel(streamKey, renderMessageId);
                
                successCount++;
            } catch (err) {
                console.log(`[TRANSFER ERROR] Failed to move ${queueName} job ID ${renderMessageId}:`, err.message);
            }
        }

        console.log(`[TRANSFER] Successfully moved ${successCount}/${messages.length} ${queueName} jobs to Upstash.`);
    } catch (error) {
        if (!error.message.includes("NOGROUP")) {
            console.log(`[TRANSFER SYSTEM ERROR - ${queueName}]`, error.message);
        }
    }
}

async function transferJobs() {
    if (isTransferring) return;
    isTransferring = true;

    const { renderText, upstashText, renderImage, upstashImage } = getClients();

    await Promise.all([
        transferQueue(renderText, upstashText, "stream:ai:text:jobs", "TEXT"),
        transferQueue(renderImage, upstashImage, "stream:ai:image:jobs", "IMAGE")
    ]);

    isTransferring = false;
}

function startJobTransfer() {
    setInterval(transferJobs, TRANSFER_RATE_MS);
}

module.exports = { startJobTransfer };
