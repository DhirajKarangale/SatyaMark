import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import os
import time
import json
import threading
import uuid
import redis
import requests
from redis.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, TimeoutError
from dotenv import load_dotenv
from flask import Flask
from starter.text_verify import verify_text

load_dotenv()

REDIS_RENDER_TEXT_URL = os.getenv("REDIS_RENDER_TEXT_URL")
REDIS_UPSTASH_TEXT_URL = os.getenv("REDIS_UPSTASH_TEXT_URL")
REDIS_RENDER_CHECK_RATE = int(os.getenv("REDIS_RENDER_CHECK_RATE"))
REDIS_UPSTASH_CHECK_RATE = int(os.getenv("REDIS_UPSTASH_CHECK_RATE"))
SELF_URL = os.getenv("SELF_URL")

WORKER_ID = uuid.uuid4().hex[:6]
CONSUMER_NAME = f"text-worker-{WORKER_ID}"

GROUP = "workers"
STREAM_KEY = "stream:ai:text:jobs"


def ensure_consumer_group(client, source_name):
    """Creates the consumer group once on startup to save quota."""
    try:
        client.xgroup_create(STREAM_KEY, GROUP, id="$", mkstream=True)
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            print(f"[{source_name}] Group creation issue: {e}")


def process_job_data(job_data, source_name):
    """Handles the AI logic and fires the webhook."""
    jobId = job_data.get("jobId")
    text = job_data.get("text")
    clientId = job_data.get("clientId")
    callback_url = job_data.get("callback_url")
    text_hash = job_data.get("text_hash")
    summary_hash = job_data.get("summary_hash")
    retry = job_data.get("retry")

    print(f"[{CONSUMER_NAME} | {source_name}] Processing Job: {jobId}")

    try:
        output = verify_text(text)
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
            "retry": retry
        }

        requests.post(callback_url, json=payload, timeout=10)
        print(f"[{CONSUMER_NAME} | {source_name}] Job completed successfully: {jobId}")
        return True

    except Exception as e:
        print(f"[{CONSUMER_NAME} | {source_name}] AI/Callback ERROR for {jobId}: {e}")
        return False


def fetch_and_process(client, source_name):
    """Fetches a job from the provided client and processes it."""
    try:
        entries = client.xreadgroup(GROUP, CONSUMER_NAME, {STREAM_KEY: ">"}, count=1)

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
            print(
                f"[{source_name}] Job {job_data.get('jobId')} failed. Leaving in PEL."
            )
            return "FAILED"

    except (ConnectionError, TimeoutError, ConnectionResetError) as e:
        raise e
    except Exception as e:
        print(f"[{source_name}] Stream Read Error: {e}")
        return "ERROR"


def render_worker_loop(redis_url, check_rate_ms):
    sleep_seconds = check_rate_ms / 1000.0
    if not redis_url:
        return

    print(f"[{CONSUMER_NAME}] Started RENDER thread (Persistent Connection).")

    retry_strategy = Retry(ExponentialBackoff(), 3)
    client = redis.from_url(
        redis_url,
        decode_responses=True,
        health_check_interval=30,
        socket_keepalive=True,
        socket_connect_timeout=10,
        socket_timeout=10,
        retry_on_timeout=True,
        retry_on_error=[ConnectionError, TimeoutError, ConnectionResetError],
        retry=retry_strategy,
    )

    ensure_consumer_group(client, "RENDER")

    while True:
        try:
            status = fetch_and_process(client, "RENDER")
            if status == "PROCESSED":
                continue

            time.sleep(sleep_seconds)

        except (
            ConnectionError,
            TimeoutError,
            ConnectionResetError,
        ) as e:
            print(f"[RENDER] Network Drop Detected: {e}. Retrying in 5s...")
            time.sleep(5)
        except Exception as e:
            print(f"[RENDER] Critical Thread Error: {e}")
            time.sleep(sleep_seconds)


def upstash_worker_loop(redis_url, check_rate_ms):
    sleep_seconds = check_rate_ms / 1000.0
    if not redis_url:
        return

    print(f"[{CONSUMER_NAME}] Started UPSTASH thread (Ephemeral Connection).")

    temp_client = redis.from_url(redis_url, decode_responses=True)
    ensure_consumer_group(temp_client, "UPSTASH")
    temp_client.close()

    while True:
        client = None
        status = "ERROR"

        try:
            client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=10,
                socket_timeout=10,
            )

            status = fetch_and_process(client, "UPSTASH")

        except (
            ConnectionError,
            TimeoutError,
            ConnectionResetError,
        ) as e:
            print(f"[UPSTASH] Ephemeral Network Error: {e}.")
        except Exception as e:
            print(f"[UPSTASH] Critical Thread Error: {e}")

        finally:
            if client:
                try:
                    client.close()
                except:
                    pass

        if status == "PROCESSED":
            continue

        time.sleep(sleep_seconds)

def process_loop():
    threads = []

    render_thread = threading.Thread(
        target=render_worker_loop,
        args=(REDIS_RENDER_TEXT_URL, REDIS_RENDER_CHECK_RATE),
        daemon=True,
    )
    render_thread.start()
    threads.append(render_thread)

    upstash_thread = threading.Thread(
        target=upstash_worker_loop,
        args=(REDIS_UPSTASH_TEXT_URL, REDIS_UPSTASH_CHECK_RATE),
        daemon=True,
    )
    upstash_thread.start()
    threads.append(upstash_thread)

    for t in threads:
        t.join()

app = Flask(__name__)

@app.route("/")
def health_check():
    return {"status": "Satyamark Text Worker is running!"}, 200

@app.route("/health")
def health_check_2():
    print("Health check")
    return {"status": "Satyamark Text Worker Health check success!"}, 200

def run_flask():
    app.run(host="0.0.0.0", port=7860)


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    process_loop()