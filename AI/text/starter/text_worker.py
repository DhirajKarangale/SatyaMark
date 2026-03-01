import os
import time
import json
import redis
import requests
from dotenv import load_dotenv
from text_verify import verify_text_summary

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
REDIS_CHECK_RATE = int(os.getenv("REDIS_CHECK_RATE", "10000"))

GROUP = "workers"
CONSUMER = "text-worker-1"
STREAM_KEY = "stream:ai:text:jobs"

r = redis.from_url(REDIS_URL, decode_responses=True)

try:
    r.xgroup_create(STREAM_KEY, GROUP, id="$", mkstream=True)
except:
    pass


def process_loop():
    print(f"[{CONSUMER}] Text Worker started...")

    while True:
        entries = r.xreadgroup(GROUP, CONSUMER, {STREAM_KEY: ">"}, count=1, block=REDIS_CHECK_RATE)

        if not entries:
            continue

        stream, messages = entries[0]
        msg_id, fields = messages[0]

        job = json.loads(fields["data"])

        text = job.get("text")
        jobId = job.get("jobId")
        clientId = job.get("clientId")
        callback_url = job.get("callback_url")
        text_hash = job.get("text_hash")
        summary_hash = job.get("summary_hash")

        print(f"[{CONSUMER}] Processing: {jobId}")

        try:
            output = verify_text_summary(text)
            summary = output.get("summary")
            result = output.get("result")

            payload = {
                "jobId": jobId,
                "clientId": clientId,
                "text_hash": text_hash,
                "summary_hash": summary_hash,
                "mark": str(result["mark"]),
                "reason": result.get("reason"),
                "confidence": result.get("confidence"),
                "urls": result.get("urls"),
                "summary":summary,
            }

            requests.post(callback_url, json=payload)
            r.xack(STREAM_KEY, GROUP, msg_id)

            print(f"[{CONSUMER}] Job completed: {jobId}")

        except Exception as e:
            print("ERROR:", e)
            time.sleep(2)


if __name__ == "__main__":
    process_loop()