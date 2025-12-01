import json
import redis

REDIS_URL = "rediss://default:AX47AAIncDJjMWVkODg0ZDcwOWU0NzEzOGNmMWRhY2NkYzU3ZjQ0YnAyMzIzMTU@perfect-satyr-32315.upstash.io:6379"
STREAM_KEY = "stream:ai:jobs"

r = redis.from_url(REDIS_URL, decode_responses=True)

job = {
    "taskId": "test-task-1",
    "userId": "u123",
    "payload": {
        "text": "Apples are not blue"  # FOR TEXT WORKER
        # "url": "https://picsum.photos/400"  # FOR IMAGE WORKERS
    },
    "callback_url": "https://webhook.site/YOUR-ID", 
    "job_token": "test-token"
}

r.xadd(STREAM_KEY, {"data": json.dumps(job)})

print("Job sent!")
