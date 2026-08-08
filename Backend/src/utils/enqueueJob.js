const { getClients } = require("../redis/redisClient");
require("dotenv").config();

const JOB_ENQUEUE_RATE = parseInt(process.env.JOB_ENQUEUE_RATE) || 1000;

class RedisQueueManager {
    constructor(queueName, renderClientName, upstashClientName, maxMemoryMB = 23) {
        this.queueName = queueName;
        this.renderClientName = renderClientName;
        this.upstashClientName = upstashClientName;
        this.maxMemoryMB = maxMemoryMB;

        this.localJobQueue = [];
        this.isProcessing = false;
    }

    async getRenderMemoryMB(client) {
        try {
            const memoryInfo = await client.info('memory');
            const match = memoryInfo.match(/used_memory:(\d+)/);
            if (match) {
                const bytes = parseInt(match[1], 10);
                return bytes / (1024 * 1024); // Convert to MB
            }
        } catch (err) {
            console.log(`[${this.queueName} MEMORY ERROR]`, err.message);
        }
        return 0;
    }

    enqueue(jobData) {
        if (!jobData.STREAM_KEY) {
            console.log(`[${this.queueName}] STREAM_KEY is undefined`);
            return;
        }

        this.localJobQueue.push(jobData);
        console.log(`[QUEUE] Job ${jobData.jobId} added to ${this.queueName} queue. (Size: ${this.localJobQueue.length})`);
    }

    async processQueue() {
        if (this.isProcessing || this.localJobQueue.length === 0) return;

        this.isProcessing = true;
        
        const clients = getClients();
        const renderClient = clients[this.renderClientName];
        const upstashClient = clients[this.upstashClientName];

        try {
            if (!renderClient) {
                console.log(`Missing Render client for ${this.queueName}`);
                return;
            }

            let usedMB = await this.getRenderMemoryMB(renderClient);

            while (this.localJobQueue.length > 0) {
                const currentJob = this.localJobQueue[0];
                const streamKey = currentJob.STREAM_KEY;
                const jobPayload = { data: JSON.stringify(currentJob) };

                if (usedMB < this.maxMemoryMB) {
                    await renderClient.xAdd(streamKey, "*", jobPayload);
                    console.log(`[${this.queueName} ROUTER] Job ${currentJob.jobId} -> RENDER (${usedMB.toFixed(2)} MB used)`);
                } else {
                    if (!upstashClient) {
                        console.log(`Missing Upstash client for ${this.queueName}`);
                        return;
                    }

                    await upstashClient.xAdd(streamKey, "*", jobPayload);
                    console.log(`[${this.queueName} ROUTER] Render Full. Job ${currentJob.jobId} -> UPSTASH`);
                }

                this.localJobQueue.shift();
            }

        } catch (error) {
            console.log(`[${this.queueName} PROCESSOR ERROR]`, error.message);
        } finally {
            this.isProcessing = false;
        }
    }

    start(intervalMs) {
        setInterval(() => this.processQueue(), intervalMs);
    }
}

const textQueue = new RedisQueueManager(
    "TEXT",
    "renderText",
    "upstashText"
);

const imageQueue = new RedisQueueManager(
    "IMAGE",
    "renderImage",
    "upstashImage"
);

async function enqueueJob(jobData) {
    if (jobData.type === "image") {
        imageQueue.enqueue(jobData);
    } else {
        textQueue.enqueue(jobData);
    }
}

function startEnqueueJob() {
    textQueue.start(JOB_ENQUEUE_RATE);
    imageQueue.start(JOB_ENQUEUE_RATE);
}

module.exports = { enqueueJob, startEnqueueJob };