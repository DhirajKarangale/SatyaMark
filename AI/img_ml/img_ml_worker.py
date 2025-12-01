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
STREAM_KEY = os.getenv("STREAM_KEY", "stream:ai:jobs")
GROUP = os.getenv("CONSUMER_GROUP", "workers")
CONSUMER = os.getenv("CONSUMER_NAME", "worker-1")
RESULT_RECEIVER = os.getenv("RESULT_RECEIVER")
HMAC_SECRET = os.getenv("JOB_HMAC_SECRET", "dev-secret")

r = redis.from_url(REDIS_URL, decode_responses=True)

try:
    r.xgroup_create(STREAM_KEY, GROUP, id="$", mkstream=True)
except:
    pass


def sign(data):
    msg = json.dumps(data, sort_keys=True)
    return hmac.new(HMAC_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()


def process_loop():
    print(f"[{CONSUMER}] Image ML Worker started...")

    while True:
        entries = r.xreadgroup(GROUP, CONSUMER, {STREAM_KEY: ">"}, count=1, block=5000)

        if not entries:
            continue

        stream, messages = entries[0]
        msg_id, fields = messages[0]

        job = json.loads(fields["data"])
        print(f"[{CONSUMER}] Processing: {job['taskId']}")

        callback_url = job.get("callback_url") or RESULT_RECEIVER

        try:
            url = job["payload"]["url"]
            result = verify_img_ml_url(url)

            payload = {
                "taskId": job["taskId"],
                "userId": job["userId"],
                "mark": result["mark"],
                "reason": result.get("reason"),
                "confidence": result.get("confidence"),
                "job_token": job["job_token"],
            }

            payload["hmac"] = sign(payload)

            requests.post(callback_url, json=payload)

            r.xack(STREAM_KEY, GROUP, msg_id)

            print(f"[{CONSUMER}] Job completed: {job['taskId']}")

        except Exception as e:
            print("ERROR:", e)
            time.sleep(2)


if __name__ == "__main__":
    process_loop()


# from AI.workers.worker_base import process_loop
# from AI.img_ml.img_ml_verify import verify_img_ml_url

# def run(job):
#     url = job["payload"]["url"]
#     result = verify_img_ml_url(url)
#     return result

# process_loop(run)
