import os
import time
import json
import redis
import requests
from dotenv import load_dotenv
from text_verify import verify_text_summary

load_dotenv()

REDIS_RENDER_TEXT_URL = os.getenv("REDIS_RENDER_TEXT_URL")
REDIS_UPSTASH_TEXT_URL = os.getenv("REDIS_UPSTASH_TEXT_URL")
REDIS_RENDER_CHECK_RATE = int(os.getenv("REDIS_RENDER_CHECK_RATE", "5000"))
REDIS_UPSTASH_CHECK_RATE = int(os.getenv("REDIS_UPSTASH_CHECK_RATE", "5000"))

GROUP = "workers"
CONSUMER = "text-worker-1"
STREAM_KEY = "stream:ai:text:jobs"


def process_job_data(job_data):
    jobId = job_data.get("jobId")
    text = job_data.get("text")
    clientId = job_data.get("clientId")
    callback_url = job_data.get("callback_url")
    text_hash = job_data.get("text_hash")
    summary_hash = job_data.get("summary_hash")

    print(f"[{CONSUMER}] Processing Job: {jobId}")

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
            "summary": summary,
        }

        requests.post(callback_url, json=payload)
        print(f"[{CONSUMER}] Job completed successfully: {jobId}")
        return True

    except Exception as e:
        print(f"[{CONSUMER}] AI Processing/Callback ERROR for {jobId}: {e}")
        return False


def fetch_and_process(redis_url, check_rate, source_name):
    if not redis_url:
        return "ERROR"

    client = redis.from_url(redis_url, decode_responses=True)

    try:
        try:
            client.xgroup_create(STREAM_KEY, GROUP, id="$", mkstream=True)
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                print(f"[{source_name}] Group creation issue: {e}")

        entries = client.xreadgroup(
            GROUP, CONSUMER, {STREAM_KEY: ">"}, count=1, block=check_rate
        )

        if not entries:
            return "EMPTY"

        stream, messages = entries[0]
        msg_id, fields = messages[0]
        job_data = json.loads(fields["data"])

        success = process_job_data(job_data)

        if success:
            client.xack(STREAM_KEY, GROUP, msg_id)
            client.xdel(STREAM_KEY, msg_id)
            return "PROCESSED"
        else:
            return "FAILED_JOB"

    except Exception as e:
        print(f"[{source_name}] Stream or Connection Error: {e}")
        return "ERROR"

    finally:
        client.close()


def process_loop():
    print(
        f"[{CONSUMER}] Text Worker started. Prioritizing Render, falling back to Upstash."
    )

    while True:
        status = fetch_and_process(
            REDIS_RENDER_TEXT_URL, REDIS_RENDER_CHECK_RATE, "RENDER"
        )

        if status == "PROCESSED":
            continue

        if status in ["EMPTY", "ERROR"]:
            if status == "ERROR":
                print(
                    f"[{CONSUMER}] Render unavailable or errored. Checking Upstash..."
                )

            upstash_status = fetch_and_process(
                REDIS_UPSTASH_TEXT_URL, REDIS_UPSTASH_CHECK_RATE, "UPSTASH"
            )

            if upstash_status == "PROCESSED":
                continue

            elif upstash_status in ["EMPTY", "ERROR"]:
                time.sleep(2)

        else:
            time.sleep(2)


if __name__ == "__main__":
    process_loop()
