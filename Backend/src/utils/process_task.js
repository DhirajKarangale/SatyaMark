require("dotenv").config();
const modelText = require('../model/modelText');
const modelImage = require('../model/modelImage');
const { enqueueJob } = require("../utils/enqueueJob");
const tracer = require("../utils/tracer");
const { generateTextHashes } = require('../hash/text_hash');
const { generateImageHash } = require('../hash/image_hash');
const { checkRateLimiter } = require("./rateLimiter");
const redisEventBus = require("../starter/redisEventBus");

const callback_url_text = process.env.RESULT_RECEIVER_TEXT;
const callback_url_image = process.env.RESULT_RECEIVER_IMG;
const STREAM_KEY_TEXT = "stream:ai:text:jobs";
const STREAM_KEY_IMAGE = "stream:ai:image:jobs";

function getTask(data, socketSessionId) {
    if (!data || !data.clientId || !data.jobId) return;

    const clientId = data.clientId;
    const jobId = data.jobId;
    const text = data.text;
    const image_url = data.image_url;

    const hasText = typeof text === "string" && text.trim().length > 0;
    const hasImage = typeof image_url === "string" && image_url.trim().length > 0;

    if (hasImage) {
        process_image(clientId, jobId, image_url, data.image_hash, socketSessionId);
        return;
    }

    if (hasText) {
        process_text(clientId, jobId, text, socketSessionId);
        return;
    }
}

async function process_text(clientId, jobId, text, socketSessionId) {
    console.log(`[TEXT] Task received → client=${clientId}, job=${jobId}`);
    
    tracer.traceEvent({
        jobId,
        sessionId: socketSessionId,
        component: "backend",
        stage: "request_handling",
        event: "request_validation_started",
        details: { type: "text", text_length: text?.length }
    });

    tracer.traceEvent({
        jobId,
        sessionId: socketSessionId,
        component: "backend",
        stage: "request_handling",
        event: "request_validation_completed",
        details: {}
    });

    tracer.traceEvent({
        jobId,
        sessionId: socketSessionId,
        component: "backend",
        stage: "hashing",
        event: "hash_generation_started",
        details: {}
    });

    const { text_hash, summary_hash } = generateTextHashes(text);

    tracer.traceEvent({
        jobId,
        sessionId: socketSessionId,
        component: "backend",
        stage: "hashing",
        event: "hash_generation_completed",
        details: {}
    });

    tracer.traceEvent({
        jobId,
        sessionId: socketSessionId,
        component: "backend",
        stage: "cache",
        event: "cache_lookup_started",
        details: {}
    });

    // CRITICAL ACCURACY FIX: Only check text_hash (exact raw match). 
    // Do NOT check summary_hash here because regex punctuation stripping can destroy meaning (e.g. "?" vs ".")
    const textData = await modelText.GetText(text_hash, summary_hash);

    tracer.traceEvent({
        jobId,
        sessionId: socketSessionId,
        component: "backend",
        stage: "cache",
        event: "cache_lookup_completed",
        details: {}
    });

    if (textData && typeof textData === "object") {
        console.log(`[TEXT] Result found in cache → job=${jobId}`);

        const payload = {
            jobId,
            clientId,
            dataId: textData.id ?? null,
            mark: textData.mark ?? null,
            confidence: textData.confidence ?? null,
            reason: textData.reason ?? null,
            urls: textData.urls ?? null,
            summary: textData.summary ?? null,
            type: "text",
        };

        tracer.traceEvent({
            jobId,
            sessionId: socketSessionId,
            component: "backend",
            stage: "cache",
            event: "cache_hit",
            details: { dataId: textData.id }
        });

        redisEventBus.publishData({ clientId, payload });
        return;
    }

    const allowed = await checkRateLimiter(clientId, socketSessionId);
    if (!allowed) {
        tracer.traceEvent({
            jobId,
            sessionId: socketSessionId,
            component: "backend",
            stage: "rate_limit",
            event: "request_rejected",
            status: "failed"
        });
        return;
    }

    tracer.traceEvent({
        jobId,
        sessionId: socketSessionId,
        component: "backend",
        stage: "cache",
        event: "cache_miss"
    });

    console.log(`[TEXT] Task enqueued → job=${jobId}`);

    await enqueueJob({
        type: "text",
        text: text,
        jobId: jobId,
        clientId: clientId,
        text_hash: text_hash,
        summary_hash: summary_hash,
        callback_url: callback_url_text,
        STREAM_KEY: STREAM_KEY_TEXT,
        retry: 0
    });
}

async function process_image(clientId, jobId, image_url, client_image_hash, socketSessionId) {
    console.log(`[IMAGE] Task received → client=${clientId}, job=${jobId}`);

    tracer.traceEvent({
        jobId,
        sessionId: socketSessionId,
        component: "backend",
        stage: "request_handling",
        event: "verification_request_received",
        details: { type: "image", image_url: image_url.length > 50 ? image_url.substring(0, 50) + "..." : image_url }
    });

    const image_hash = client_image_hash || await generateImageHash(image_url);
    const imageData = await modelImage.GetImage(image_url, image_hash);

    if (imageData && typeof imageData === "object") {
        console.log(`[IMAGE] Result found in cache → job=${jobId}`);

        const payload = {
            jobId,
            clientId,
            dataId: imageData.id ?? null,
            mark: imageData.mark ?? null,
            confidence: imageData.confidence ?? null,
            reason: imageData.reason ?? null,
            image_url: imageData.image_url ?? null,
            type: "image",
        };

        tracer.traceEvent({
            jobId,
            sessionId: socketSessionId,
            component: "backend",
            stage: "cache",
            event: "cache_hit",
            details: { dataId: imageData.id }
        });

        redisEventBus.publishData({ clientId, payload });
        return;
    }

    const allowed = await checkRateLimiter(clientId, socketSessionId);
    if (!allowed) {
        tracer.traceEvent({
            jobId,
            sessionId: socketSessionId,
            component: "backend",
            stage: "rate_limit",
            event: "request_rejected",
            status: "failed"
        });
        return;
    }

    tracer.traceEvent({
        jobId,
        sessionId: socketSessionId,
        component: "backend",
        stage: "cache",
        event: "cache_miss"
    });

    console.log(`[IMAGE] Task enqueued → job=${jobId}`);
    await enqueueJob({
        type: "image",
        jobId: jobId,
        clientId: clientId,
        image_url: image_url,
        image_hash: image_hash,
        callback_url: callback_url_image,
        STREAM_KEY: STREAM_KEY_IMAGE,
        retry: 0
    });
}

module.exports = { getTask }