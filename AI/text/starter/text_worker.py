import os
import time
import json
import redis
import requests
import threading
from dotenv import load_dotenv
from text.starter.text_verify import verify_text_summary

load_dotenv()

REDIS_RENDER_TEXT_URL = os.getenv("REDIS_RENDER_TEXT_URL")
REDIS_UPSTASH_TEXT_URL = os.getenv("REDIS_UPSTASH_TEXT_URL")
REDIS_RENDER_CHECK_RATE = int(os.getenv("REDIS_RENDER_CHECK_RATE"))
REDIS_UPSTASH_CHECK_RATE = int(os.getenv("REDIS_UPSTASH_CHECK_RATE"))

GROUP = "workers"
CONSUMER = "text-worker-1"
STREAM_KEY = "stream:ai:text:jobs"


def process_job_data(job_data, source_name):
    jobId = job_data.get("jobId")
    text = job_data.get("text")
    clientId = job_data.get("clientId")
    callback_url = job_data.get("callback_url")
    text_hash = job_data.get("text_hash")
    summary_hash = job_data.get("summary_hash")

    print(f"[{CONSUMER} | {source_name}] Processing Job: {jobId}")

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
        print(f"[{CONSUMER} | {source_name}] Job completed successfully: {jobId}")
        return True

    except Exception as e:
        print(
            f"[{CONSUMER} | {source_name}] AI Processing/Callback ERROR for {jobId}: {e}"
        )
        return False


def fetch_and_process(redis_url, source_name):
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
            GROUP, CONSUMER, {STREAM_KEY: ">"}, count=1
        )

        if not entries:
            return "EMPTY"

        stream, messages = entries[0]
        msg_id, fields = messages[0]
        job_data = json.loads(fields["data"])

        success = process_job_data(job_data, source_name)

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


def worker_loop(redis_url, check_rate_ms, source_name):
    """This runs in its own thread, managing its own sleep schedule."""
    sleep_seconds = check_rate_ms / 1000.0

    print(
        f"[{CONSUMER}] Started {source_name} polling thread (Wakes up every {sleep_seconds}s)."
    )

    while True:
        status = fetch_and_process(redis_url, source_name)

        if status == "PROCESSED":
            continue

        time.sleep(sleep_seconds)


def process_loop():
    print(f"[{CONSUMER}] Starting Disconnected Polling Worker...")

    threads = []

    render_thread = threading.Thread(
        target=worker_loop,
        args=(REDIS_RENDER_TEXT_URL, REDIS_RENDER_CHECK_RATE, "RENDER"),
        daemon=True,
    )
    render_thread.start()
    threads.append(render_thread)

    upstash_thread = threading.Thread(
        target=worker_loop,
        args=(REDIS_UPSTASH_TEXT_URL, REDIS_UPSTASH_CHECK_RATE, "UPSTASH"),
        daemon=True,
    )
    upstash_thread.start()
    threads.append(upstash_thread)

    for t in threads:
        t.join()


if __name__ == "__main__":
    process_loop()
