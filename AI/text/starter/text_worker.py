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
import logging
from redis.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, TimeoutError
from dotenv import load_dotenv
from starter.text_verify import verify_text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

REDIS_RENDER_TEXT_URL = os.getenv("REDIS_RENDER_TEXT_URL")
REDIS_UPSTASH_TEXT_URL = os.getenv("REDIS_UPSTASH_TEXT_URL")
REDIS_RENDER_CHECK_RATE = int(os.getenv("REDIS_RENDER_CHECK_RATE", 1000))
REDIS_UPSTASH_CHECK_RATE = int(os.getenv("REDIS_UPSTASH_CHECK_RATE", 1000))
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
            logger.warning(f"[{source_name}] Group creation issue: {e}")


def process_job_data(job_data, source_name):
    """Handles the AI logic and fires the webhook."""
    jobId = job_data.get("jobId")
    text = job_data.get("text")
    clientId = job_data.get("clientId")
    callback_url = job_data.get("callback_url")
    text_hash = job_data.get("text_hash")
    summary_hash = job_data.get("summary_hash")
    retry = job_data.get("retry")

    logger.info(f"[{CONSUMER_NAME} | {source_name}] Processing Job: {jobId}")

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

        requests.post(callback_url, json=payload, timeout=25)
        logger.info(f"[{CONSUMER_NAME} | {source_name}] Job completed successfully: {jobId}")
        return True

    except Exception as e:
        logger.error(f"[{CONSUMER_NAME} | {source_name}] AI/Callback ERROR for {jobId}: {e}", exc_info=True)
        return False

def process_pel(client, source_name):
    """Processes any abandoned jobs left in the PEL due to network drops."""
    try:
        entries = client.xreadgroup(GROUP, CONSUMER_NAME, {STREAM_KEY: "0"}, count=1)
        if not entries:
            return

        stream, messages = entries[0]
        if not messages:
            return

        msg_id, fields = messages[0]
        job_data = json.loads(fields["data"])
        
        logger.info(f"[{source_name}] Recovered job {job_data.get('jobId')} from PEL.")

        success = process_job_data(job_data, source_name)
        if success:
            client.xack(STREAM_KEY, GROUP, msg_id)
            client.xdel(STREAM_KEY, msg_id)

    except (ConnectionError, TimeoutError, ConnectionResetError) as e:
        raise e
    except Exception as e:
        logger.error(f"[{source_name}] PEL Read Error: {e}", exc_info=True)


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
            logger.warning(f"[{source_name}] Job {job_data.get('jobId')} failed. Leaving in PEL.")
            return "FAILED"

    except (ConnectionError, TimeoutError, ConnectionResetError) as e:
        raise e
    except Exception as e:
        logger.error(f"[{source_name}] Stream Read Error: {e}", exc_info=True)
        return "ERROR"


def worker_loop(redis_url, check_rate_ms, source_name):
    sleep_seconds = check_rate_ms / 1000.0
    if not redis_url:
        return

    logger.info(f"[{CONSUMER_NAME}] Started {source_name} thread (Persistent Connection).")

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

    ensure_consumer_group(client, source_name)

    while True:
        try:
            process_pel(client, source_name)
            status = fetch_and_process(client, source_name)
            if status == "PROCESSED":
                continue

            time.sleep(sleep_seconds)

        except (ConnectionError, TimeoutError, ConnectionResetError) as e:
            logger.warning(f"[{source_name}] Network Drop Detected: {e}. Retrying in 5s...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"[{source_name}] Critical Thread Error: {e}", exc_info=True)
            time.sleep(sleep_seconds)

def process_loop():
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
