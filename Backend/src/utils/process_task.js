require("dotenv").config();
const modelText = require('../model/modelText');
const modelImage = require('../model/modelImage');
const { enqueueJob } = require("../utils/enqueueJob");
const { generateTextHashes } = require('../hash/text_hash');
const { generateImageHash } = require('../hash/image_hash');
const eventBus = require("../starter/eventBus");

const callback_url_text = process.env.RESULT_RECEIVER_TEXT;
const callback_url_image = process.env.RESULT_RECEIVER_IMG;
const STREAM_KEY_TEXT = "stream:ai:text:jobs";
const STREAM_KEY_IMAGE_ML = "stream:ai:imageml:jobs";
const STREAM_KEY_IMAGE_Forensic = "stream:ai:imageforensic:jobs";

function getTask(data) {
    const clientId = data.clientId;
    const jobId = data.jobId;
    const text = data.text;
    const image_url = data.image_url;

    if (image_url) process_image(clientId, jobId, image_url);
    else if (text) process_text(clientId, jobId, text);
}

async function process_text(clientId, jobId, text) {
    const { text_hash, summary_hash } = generateTextHashes(text)
    const textData = await modelText.GetText(text_hash, summary_hash);

    if (textData) {
        const payload = {
            jobId,
            clientId,
            text_hash: textData.text_hash,
            summary_hash: textData.summary_hash,
            mark: textData.mark,
            reason: textData.reason,
            confidence: Number(textData.confidence),
            urls: textData.urls
        };

        eventBus.emit("sendData", { clientId, payload });
        return;
    }

    await enqueueJob({
        text: text,
        jobId: jobId,
        clientId: clientId,
        text_hash: text_hash,
        summary_hash: summary_hash,
        callback_url: callback_url_text,
        STREAM_KEY: STREAM_KEY_TEXT
    });
}

async function process_image(clientId, jobId, image_url) {
    const { image_hash } = await generateImageHash(image_url)
    const imageData = await modelImage.GetImage(image_url, image_hash);

    if (imageData) {
        const payload = {
            jobId,
            clientId,
            image_url: imageData.image_url,
            image_hash: imageData.image_hash,
            mark: imageData.mark,
            reason: imageData.reason,
            confidence: Number(imageData.confidence),
        };

        eventBus.emit("sendData", { clientId, payload });
        return;
    }

    await enqueueJob({
        jobId: jobId,
        clientId: clientId,
        image_url: image_url,
        image_hash: image_hash,
        callback_url: callback_url_image,
        STREAM_KEY: STREAM_KEY_IMAGE_Forensic
    });
}

module.exports = { getTask }