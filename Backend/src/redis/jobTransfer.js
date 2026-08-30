require("dotenv").config();
const { getClients } = require("./redisClient");
const connectionManager = require("../utils/connectionManager");

const TRANSFER_RATE_MS = parseInt(process.env.REDIS_RENDER_UPSTASH_TRANSFER_RATE) || 60000;

const GROUP_NAME = "workers";
const CONSUMER_NAME = "transfer-node-script";

let isTransferring = false;

async function transferQueue(renderClient, upstashClient, streamKey, queueName) {
    if (!renderClient || !upstashClient) return;

    // Issue 19: Only transfer if Upstash is confirmed connected to prevent data loss
    const upstashConnName = queueName === "TEXT" ? "Upstash Text" : "Upstash Image";
    if (!connectionManager.isConnected(upstashConnName)) return;

    try {
        const response = await renderClient.xReadGroup(
            GROUP_NAME,
            CONSUMER_NAME,
            [{ key: streamKey, id: ">" }],
            { COUNT: 50 }  // Issue 19: Reduced from 500 to limit blast radius
        );

        if (!response || response.length === 0) return;
        const messages = response[0].messages;
        if (!messages || messages.length === 0) return;

        console.log(`[TRANSFER] Found ${messages.length} unassigned jobs in ${queueName}. Moving to Upstash...`);

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
                // Issue 19: If Upstash write fails, stop to prevent claiming without transferring
                console.log(`[TRANSFER ERROR] Failed to move ${queueName} job ${renderMessageId}. Stopping transfer.`, err.message);
                break;
            }
        }

        if (successCount > 0) {
            console.log(`[TRANSFER] Successfully moved ${successCount}/${messages.length} ${queueName} jobs to Upstash.`);
        }
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
