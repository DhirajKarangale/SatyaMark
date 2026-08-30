const { getClients } = require("../redis/redisClient");
const connectionManager = require("./connectionManager");
const tracer = require("./tracer");
require("dotenv").config();

const JOB_ENQUEUE_RATE = parseInt(process.env.JOB_ENQUEUE_RATE) || 1000;

class RedisQueueManager {
    constructor(queueName, renderClientName, upstashClientName, renderConnName, upstashConnName, maxMemoryMB = 23) {
        this.queueName = queueName;
        this.renderClientName = renderClientName;
        this.upstashClientName = upstashClientName;
        this.renderConnName = renderConnName;
        this.upstashConnName = upstashConnName;
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
                return bytes / (1024 * 1024);
            }
        } catch (err) {
            // Memory check failed — treat as full so we fall through to Upstash
        }
        return Infinity;
    }

    enqueue(jobData) {
        if (!jobData.STREAM_KEY) {
            console.log(`[${this.queueName}] STREAM_KEY is undefined`);
            return;
        }

        this.localJobQueue.push(jobData);
    }

    async processQueue() {
        if (this.isProcessing || this.localJobQueue.length === 0) return;

        // Non-blocking pre-check: skip if no Redis is connected.
        // This prevents the Proxy's ensureConnection() from blocking indefinitely.
        const renderReady = connectionManager.getStatus(this.renderConnName) === 'connected';
        const upstashReady = connectionManager.getStatus(this.upstashConnName) === 'connected';

        if (!renderReady && !upstashReady) return;

        this.isProcessing = true;

        const clients = getClients();
        const renderClient = clients[this.renderClientName];
        const upstashClient = clients[this.upstashClientName];

        try {
            let usedMB = Infinity;

            if (renderReady && renderClient) {
                usedMB = await this.getRenderMemoryMB(renderClient);
            }

            while (this.localJobQueue.length > 0) {
                const currentJob = this.localJobQueue[0];
                const streamKey = currentJob.STREAM_KEY;
                const jobPayload = { data: JSON.stringify(currentJob) };

                let pushed = false;

                // Try Render first (if connected and under memory limit)
                if (renderReady && renderClient && usedMB < this.maxMemoryMB) {
                    try {
                        tracer.traceEvent({
                            jobId: currentJob.jobId,
                            component: "redis",
                            stage: "queue",
                            event: "redis_instance_selected",
                            details: { instance: "RENDER", usedMB }
                        });
                        
                        tracer.traceEvent({
                            jobId: currentJob.jobId,
                            component: "redis",
                            stage: "queue",
                            event: "xadd_started",
                            details: { streamKey }
                        });
                        
                        const redisJobId = await renderClient.xAdd(streamKey, "*", jobPayload);
                        console.log(`[${this.queueName}] Job ${currentJob.jobId} → RENDER`);
                        
                        tracer.traceEvent({
                            jobId: currentJob.jobId,
                            component: "redis",
                            stage: "queue",
                            event: "xadd_completed",
                            details: { redis: "RENDER", streamKey, memoryMB: usedMB, redisJobId }
                        });
                        pushed = true;
                    } catch (err) {
                        // Render failed mid-operation, fall through to Upstash
                    }
                }

                if (!pushed && upstashReady && upstashClient) {
                    try {
                        tracer.traceEvent({
                            jobId: currentJob.jobId,
                            component: "redis",
                            stage: "queue",
                            event: "redis_instance_selected",
                            details: { instance: "UPSTASH" }
                        });

                        tracer.traceEvent({
                            jobId: currentJob.jobId,
                            component: "redis",
                            stage: "queue",
                            event: "xadd_started",
                            details: { streamKey }
                        });

                        const redisJobId = await upstashClient.xAdd(streamKey, "*", jobPayload);
                        console.log(`[${this.queueName}] Job ${currentJob.jobId} → UPSTASH`);
                        
                        tracer.traceEvent({
                            jobId: currentJob.jobId,
                            component: "redis",
                            stage: "queue",
                            event: "xadd_completed",
                            details: { redis: "UPSTASH", streamKey, redisJobId }
                        });
                        pushed = true;
                    } catch (err) {
                        // Both clusters failed
                    }
                }

                if (!pushed) {
                    break; // No Redis available right now, retry on next interval tick
                }

                this.localJobQueue.shift();
            }

        } catch (error) {
            console.log(`[${this.queueName} ERROR]`, error.message);
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
    "upstashText",
    "Render Text",
    "Upstash Text"
);

const imageQueue = new RedisQueueManager(
    "IMAGE",
    "renderImage",
    "upstashImage",
    "Render Image",
    "Upstash Image"
);

async function enqueueJob(jobData) {
    tracer.traceEvent({
        jobId: jobData.jobId,
        component: "backend",
        stage: "queue",
        event: "queue_selection_started",
        details: { type: jobData.type }
    });

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