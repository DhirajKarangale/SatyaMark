import os
import time
import json
import redis
import requests
import hmac
import hashlib
from dotenv import load_dotenv
from AI.img_ml.img_ml_verify import verify_img_ml_url

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

GROUP = "workers"
CONSUMER = "image-ml-worker-1"
STREAM_KEY = "stream:ai:imageml:jobs"

r = redis.from_url(REDIS_URL, decode_responses=True)

try:
    r.xgroup_create(STREAM_KEY, GROUP, id="$", mkstream=True)
except:
    pass


def process_loop():
    print(f"[{CONSUMER}] Image ML Worker started...")

    while True:
        entries = r.xreadgroup(GROUP, CONSUMER, {STREAM_KEY: ">"}, count=1, block=5000)

        if not entries:
            continue

        stream, messages = entries[0]
        msg_id, fields = messages[0]

        job = json.loads(fields["data"])

        jobId = job.get("jobId")
        clientId = job.get("clientId")
        callback_url = job.get("callback_url")
        image_url = job.get("image_url")
        image_hash = job.get("image_hash")

        print(f"[{CONSUMER}] Processing: {jobId}")

        try:
            url = image_url
            result = verify_img_ml_url(url)

            payload = {
                "jobId": jobId,
                "clientId": clientId,
                "image_url": image_url,
                "image_hash": image_hash,
                "mark": str(result["mark"]),
                "reason": result.get("reason"),
                "confidence": result.get("confidence"),
            }

            requests.post(callback_url, json=payload)

            r.xack(STREAM_KEY, GROUP, msg_id)

            print(f"[{CONSUMER}] Job completed: {jobId}")

        except Exception as e:
            print("ERROR:", e)
            time.sleep(2)


if __name__ == "__main__":
    process_loop()
