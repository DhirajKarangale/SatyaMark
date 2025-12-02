require("dotenv").config();
const modelHash = require('../model/modelHash');
const { enqueueJob } = require("../utils/enqueueJob");
const { sendData } = require("../starter/ws-server");
const { generateTextHashes } = require('../hash/text_hash');

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
    const { originalHash, summaryHash } = generateTextHashes(text)
    const textData = await modelHash.GetText(originalHash, summaryHash);

    if (textData) {
        sendData(textData);
        return;
    }

    await enqueueJob({
        text: text,
        jobId: jobId,
        clientId: clientId,
        callback_url: callback_url_text,
    });
}

function process_image(clientId, jobId, image_url) {

}

module.exports = { getTask }