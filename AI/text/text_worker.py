import os
import time
import json
import redis
import requests
from dotenv import load_dotenv
from text_verify import verify_text_summary
from connect import connect_llms

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

STREAM_KEY = "stream:ai:text:jobs"
GROUP = "workers"
CONSUMER = "text-worker-1"

READ_COUNT = 5
BLOCK_TIME_MS = 60000
MAX_IDLE_SLEEP = 60
PENDING_IDLE_MS = 60000

r = redis.from_url(REDIS_URL, decode_responses=True)

try:
    r.xgroup_create(STREAM_KEY, GROUP, id="$", mkstream=True)
except redis.exceptions.ResponseError:
    pass


def recover_pending():
    try:
        pending = r.xpending_range(STREAM_KEY, GROUP, "-", "+", 10, CONSUMER)

        if pending:
            msg_ids = [p["message_id"] for p in pending]
            r.xclaim(
                STREAM_KEY,
                GROUP,
                CONSUMER,
                min_idle_time=PENDING_IDLE_MS,
                message_ids=msg_ids,
            )
            print(f"[{CONSUMER}] Recovered {len(msg_ids)} pending jobs")

    except Exception as e:
        print("Pending recovery failed:", e)


def process_loop():
    print(f"[{CONSUMER}] Text Worker started...")
    connect_llms()
    recover_pending()

    idle_sleep = 1

    while True:
        entries = r.xreadgroup(
            GROUP, CONSUMER, {STREAM_KEY: ">"}, count=READ_COUNT, block=BLOCK_TIME_MS
        )

        if not entries:
            idle_sleep = min(idle_sleep * 2, MAX_IDLE_SLEEP)
            time.sleep(idle_sleep)
            continue

        idle_sleep = 1

        stream, messages = entries[0]

        for msg_id, fields in messages:
            try:
                job = json.loads(fields["data"])

                text = job.get("text")
                jobId = job.get("jobId")
                clientId = job.get("clientId")
                callback_url = job.get("callback_url")

                print(f"[{CONSUMER}] Processing: {jobId}")

                output = verify_text_summary(text)
                summary = output.get("summary")
                result = output.get("result")

                payload = {
                    "jobId": jobId,
                    "clientId": clientId,
                    "text_hash": job.get("text_hash"),
                    "summary_hash": job.get("summary_hash"),
                    "mark": str(result["mark"]),
                    "reason": result.get("reason"),
                    "confidence": result.get("confidence"),
                    "urls": result.get("urls"),
                    "summary": summary,
                }

                requests.post(callback_url, json=payload, timeout=10)

                r.xack(STREAM_KEY, GROUP, msg_id)

                print(f"[{CONSUMER}] Job completed: {jobId}")

            except Exception as e:
                print(f"[{CONSUMER}] ERROR processing job:", e)
                time.sleep(2)


if __name__ == "__main__":
    process_loop()
