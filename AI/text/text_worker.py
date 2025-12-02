import os
import time
import json
import redis
import requests
from dotenv import load_dotenv
from AI.text.text_verify import verify_text

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
STREAM_KEY = os.getenv("STREAM_KEY", "stream:ai:jobs")
GROUP = os.getenv("CONSUMER_GROUP", "workers")
CONSUMER = os.getenv("CONSUMER_NAME", "worker-1")

r = redis.from_url(REDIS_URL, decode_responses=True)

try:
    r.xgroup_create(STREAM_KEY, GROUP, id="$", mkstream=True)
except:
    pass


def process_loop():
    print(f"[{CONSUMER}] Text Worker started...")

    while True:
        entries = r.xreadgroup(GROUP, CONSUMER, {STREAM_KEY: ">"}, count=1, block=5000)

        if not entries:
            continue

        stream, messages = entries[0]
        msg_id, fields = messages[0]

        job = json.loads(fields["data"])
        print(fields)

        text = job.get("text")
        jobId = job.get("jobId")
        clientId = job.get("clientId")
        callback_url = job.get("callback_url")

        print(f"[{CONSUMER}] Processing: {jobId}")

        try:
            result = verify_text(text)

            payload = {
                "jobId": jobId,
                "clientId": clientId,
                "mark": str(result["mark"]),
                "reason": result.get("reason"),
                "confidence": result.get("confidence"),
                "urls": result.get("urls"),
            }

            requests.post(callback_url, json=payload)
            r.xack(STREAM_KEY, GROUP, msg_id)

            print(f"[{CONSUMER}] Job completed: {jobId}")

        except Exception as e:
            print("ERROR:", e)
            time.sleep(2)


if __name__ == "__main__":
    process_loop()
