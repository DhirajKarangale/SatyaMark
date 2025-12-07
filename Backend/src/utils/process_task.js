require("dotenv").config();
const modelText = require('../model/modelText');
const modelImage = require('../model/modelImage');
const { enqueueJob } = require("../utils/enqueueJob");
const { generateTextHashes } = require('../hash/text_hash');
const { generateImageHash } = require('../hash/image_hash');
const eventBus = require("../starter/eventBus");

const IMAGE_ALGO = process.env.IMAGE_ALGO;
const callback_url_text = process.env.RESULT_RECEIVER_TEXT;
const callback_url_image = process.env.RESULT_RECEIVER_IMG;
const STREAM_KEY_TEXT = "stream:ai:text:jobs";
const STREAM_KEY_IMAGE_ML = "stream:ai:imageml:jobs";
const STREAM_KEY_IMAGE_Forensic = "stream:ai:imageforensic:jobs";
let STREAM_KEY_IMAGE = STREAM_KEY_IMAGE_Forensic;

if (IMAGE_ALGO && IMAGE_ALGO.toLowerCase() == "ml") STREAM_KEY_IMAGE = STREAM_KEY_IMAGE_ML;

function getTask(data) {
    const clientId = data.clientId;
    const jobId = data.jobId;
    const text = data.text;
    const image_url = data.image_url;

    if (image_url) process_image(clientId, jobId, image_url);
    else if (text) process_text(clientId, jobId, text);
}

async function process_text(clientId, jobId, text) {
    console.log(`[TEXT] Task received → client=${clientId}, job=${jobId}`);

    const { text_hash, summary_hash } = generateTextHashes(text)
    const textData = await modelText.GetText(text_hash, summary_hash);

    if (textData) {
        console.log(`[TEXT] Result found in cache → job=${jobId}: `);

        const payload = {
            jobId,
            clientId,
            dataId: textData.id,
            mark: textData.mark,
        };

        eventBus.emit("sendData", { clientId, payload });
        return;
    }

    console.log(`[TEXT] Task enqueued → job=${jobId}`);

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
    console.log(`[IMAGE] Task received → client=${clientId}, job=${jobId}`);

    const { image_hash } = await generateImageHash(image_url)
    const imageData = await modelImage.GetImage(image_url, image_hash);

    if (imageData) {
        console.log(`[IMAGE] Result found in cache → job=${jobId}`);

        const payload = {
            jobId,
            clientId,
            dataId: imageData.id,
            mark: imageData.mark,
        };

        eventBus.emit("sendData", { clientId, payload });
        return;
    }

    console.log(`[IMAGE] Task enqueued → job=${jobId}, algo=${IMAGE_ALGO}`);
    await enqueueJob({
        jobId: jobId,
        clientId: clientId,
        image_url: image_url,
        image_hash: image_hash,
        callback_url: callback_url_image,
        STREAM_KEY: STREAM_KEY_IMAGE
    });
}

module.exports = { getTask }