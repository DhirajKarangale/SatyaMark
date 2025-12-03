const { v4: uuidv4 } = require("uuid");
const redis = require("../redis/redis");

function generateJobToken() {
    return uuidv4() + ":" + Date.now();
}

async function enqueueJob({ text, jobId, clientId, callback_url, image_url, text_hash, summary_hash, image_hash, STREAM_KEY }) {
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

    await redis.xAdd(STREAM_KEY, "*", {
        data: JSON.stringify(job),
    });

    return { taskId, job_token };
}

module.exports = { enqueueJob };