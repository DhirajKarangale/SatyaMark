const { v4: uuidv4 } = require("uuid");
const redis = require("../redis/redis");

const STREAM_KEY = process.env.STREAM_KEY || "stream:ai:jobs";

function generateJobToken() {
    return uuidv4() + ":" + Date.now(); 
}

async function enqueueJob({ text, jobId, clientId, callback_url, image_url }) {
    const taskId = uuidv4();
    const job_token = generateJobToken();

    const job = {
        text,
        jobId,
        clientId,
        callback_url,
        image_url
    };

    await redis.xAdd(STREAM_KEY, "*", {
        data: JSON.stringify(job),
    });

    return { taskId, job_token };
}

module.exports = { enqueueJob };