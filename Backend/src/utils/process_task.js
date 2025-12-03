require("dotenv").config();
const modelText = require('../model/modelText');
const { enqueueJob } = require("../utils/enqueueJob");
const { generateTextHashes } = require('../hash/text_hash');
const eventBus = require("../starter/eventBus");

const callback_url_text = process.env.RESULT_RECEIVER_TEXT;

function getTask(data) {
    const clientId = data.clientId;
    const jobId = data.jobId;
    const text = data.text;
    const image_url = data.image_url;

    if (text) process_text(clientId, jobId, text);
    else if (image_url) process_image(clientId, jobId, image_url);
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
    });
}

function process_image(clientId, jobId, image_url) {

}

module.exports = { getTask }