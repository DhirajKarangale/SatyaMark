const redis = require("redis");
require("dotenv").config();

const JOB_ENQUEUE_RATE = parseInt(process.env.JOB_ENQUEUE_RATE);
const REDIS_RENDER_TEXT_URL = process.env.REDIS_RENDER_TEXT_URL;
const REDIS_UPSTASH_TEXT_URL = process.env.REDIS_UPSTASH_TEXT_URL;
const REDIS_RENDER_IMAGE_URL = process.env.REDIS_RENDER_IMAGE_URL;
const REDIS_UPSTASH_IMAGE_URL = process.env.REDIS_UPSTASH_IMAGE_URL;

class RedisQueueManager {
    constructor(queueName, renderUrl, upstashUrl, maxMemoryMB = 23) {
        this.queueName = queueName;
        this.renderUrl = renderUrl;
        this.upstashUrl = upstashUrl;
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
        let renderClient = null;
        let upstashClient = null;

        try {
            if (!this.renderUrl) {
                console.log(`Missing Render URL for ${this.queueName}`);
                return;
            };

            renderClient = redis.createClient({ url: this.renderUrl });
            renderClient.on("error", (e) => console.log(`[${this.queueName} RENDER ERROR]`, e.message));
            await renderClient.connect();

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
                        if (!this.upstashUrl) {
                            console.log(`Missing Upstash URL for ${this.queueName}`);
                            return;
                        }
                        upstashClient = redis.createClient({ url: this.upstashUrl });
                        upstashClient.on("error", (e) => console.log(`[${this.queueName} UPSTASH ERROR]`, e.message));
                        await upstashClient.connect();
                    }

                    await upstashClient.xAdd(streamKey, "*", jobPayload);
                    console.log(`[${this.queueName} ROUTER] Render Full. Job ${currentJob.jobId} -> UPSTASH`);
                }

                this.localJobQueue.shift();
            }

        } catch (error) {
            console.log(`[${this.queueName} PROCESSOR ERROR]`, error.message);
        } finally {
            try {
                if (renderClient && renderClient.isOpen) await renderClient.quit();
                if (upstashClient && upstashClient.isOpen) await upstashClient.quit();
            } catch (closeErr) {
                console.log(`[${this.queueName} CLOSE ERROR]`, closeErr.message);
            }
            this.isProcessing = false;
        }
    }

    start(intervalMs) {
        setInterval(() => this.processQueue(), intervalMs);
    }
}

const textQueue = new RedisQueueManager(
    "TEXT",
    REDIS_RENDER_TEXT_URL,
    REDIS_UPSTASH_TEXT_URL
);

const imageQueue = new RedisQueueManager(
    "IMAGE",
    REDIS_RENDER_IMAGE_URL,
    REDIS_UPSTASH_IMAGE_URL
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