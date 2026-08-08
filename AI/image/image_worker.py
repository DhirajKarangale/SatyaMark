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
from image.image_verify import verify

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

REDIS_RENDER_IMAGE_URL = os.getenv("REDIS_RENDER_IMAGE_URL")
REDIS_UPSTASH_IMAGE_URL = os.getenv("REDIS_UPSTASH_IMAGE_URL")
REDIS_RENDER_CHECK_RATE = int(os.getenv("REDIS_RENDER_CHECK_RATE", 1000))
REDIS_UPSTASH_CHECK_RATE = int(os.getenv("REDIS_UPSTASH_CHECK_RATE", 1000))

WORKER_ID = uuid.uuid4().hex[:6]
CONSUMER_NAME = f"image-worker-{WORKER_ID}"

GROUP = "workers"
STREAM_KEY = "stream:ai:image:jobs"


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
    clientId = job_data.get("clientId")
    callback_url = job_data.get("callback_url")
    image_url = job_data.get("image_url")
    image_hash = job_data.get("image_hash")
    retry = job_data.get("retry")

    logger.info(f"[{CONSUMER_NAME} | {source_name}] Processing Job: {jobId}")

    try:
        result = verify(image_url)

        payload = {
            "jobId": jobId,
            "clientId": clientId,
            "image_url": image_url,
            "image_hash": image_hash,
            "mark": str(result["mark"]),
            "reason": result.get("reason"),
            "confidence": result.get("confidence"),
            "retry": retry
        }

        requests.post(callback_url, json=payload, timeout=10)
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


def render_worker_loop(redis_url, check_rate_ms):
    sleep_seconds = check_rate_ms / 1000.0
    if not redis_url:
        return

    logger.info(f"[{CONSUMER_NAME}] Started RENDER thread (Persistent Connection).")

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
            process_pel(client, "RENDER")
            status = fetch_and_process(client, "RENDER")
            if status == "PROCESSED":
                continue

            time.sleep(sleep_seconds)

        except (ConnectionError, TimeoutError, ConnectionResetError) as e:
            logger.warning(f"[RENDER] Network Drop Detected: {e}. Retrying in 5s...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"[RENDER] Critical Thread Error: {e}", exc_info=True)
            time.sleep(sleep_seconds)


def upstash_worker_loop(redis_url, check_rate_ms):
    sleep_seconds = check_rate_ms / 1000.0
    if not redis_url:
        return

    logger.info(f"[{CONSUMER_NAME}] Started UPSTASH thread (Ephemeral Connection).")

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

            process_pel(client, "UPSTASH")
            status = fetch_and_process(client, "UPSTASH")

        except (ConnectionError, TimeoutError, ConnectionResetError) as e:
            logger.warning(f"[UPSTASH] Ephemeral Network Error: {e}.")
        except Exception as e:
            logger.error(f"[UPSTASH] Critical Thread Error: {e}", exc_info=True)

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
        args=(REDIS_RENDER_IMAGE_URL, REDIS_RENDER_CHECK_RATE),
        daemon=True,
    )
    render_thread.start()
    threads.append(render_thread)

    upstash_thread = threading.Thread(
        target=upstash_worker_loop,
        args=(REDIS_UPSTASH_IMAGE_URL, REDIS_UPSTASH_CHECK_RATE),
        daemon=True,
    )
    upstash_thread.start()
    threads.append(upstash_thread)

    for t in threads:
        t.join()

if __name__ == "__main__":
    process_loop()