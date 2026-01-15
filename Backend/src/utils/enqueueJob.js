const { v4: uuidv4 } = require("uuid");
const { imageRedis, ready: imageReady } = require("../redis/redisImage");
const { textRedis, ready: textReady } = require("../redis/redisText");

function generateJobToken() {
    return uuidv4() + ":" + Date.now();
}

async function enqueueJob({ type, text, jobId, clientId, callback_url, image_url, text_hash, summary_hash, image_hash, STREAM_KEY }) {
    if (!STREAM_KEY) {
        console.log("STREAM_KEY is undefined");
        return;
    }

    const taskId = uuidv4();
    const job_token = generateJobToken();

    const job = {
        text,
        jobId,
        clientId,
        callback_url,
        text_hash,
        summary_hash,
        image_url,
        image_hash
    };

    try {
        const redisClient = type === "image" ? imageRedis : textRedis;
        const ready = type === "image" ? imageReady : textReady;
        
        await ready;
        await redisClient.xAdd(STREAM_KEY, "*", { data: JSON.stringify(job), });
    } catch (err) {
        console.log("Redis xAdd failed:", err.message);
        throw err;
    }

    return { taskId, job_token };
}

module.exports = { enqueueJob };