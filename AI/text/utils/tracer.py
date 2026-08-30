import contextvars
import requests
import logging
from typing import Optional, Any, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

job_id_var = contextvars.ContextVar("job_id", default=None)
session_id_var = contextvars.ContextVar("session_id", default=None)
backend_url_var = contextvars.ContextVar("backend_url", default=None)

def trace_event(
    component: str,
    stage: str,
    event: str,
    status: str = "success",
    duration_ms: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None
):
    job_id = job_id_var.get()
    backend_url = backend_url_var.get()

    # If trace context isn't set (e.g. tracing is essentially disabled or uninitialized for this thread)
    if not job_id or not backend_url:
        return

    details_payload = details or {}
    details_payload["timestamp"] = datetime.utcnow().isoformat() + "Z"

    payload = {
        "jobId": job_id,
        "sessionId": session_id_var.get(),
        "component": component,
        "stage": stage,
        "event": event,
        "status": status,
        "duration_ms": duration_ms,
        "details": details_payload
    }

    try:
        url = f"{backend_url}/trace-event"
        # Fire and forget with short timeout
        requests.post(url, json=payload, timeout=2.0)
    except Exception as e:
        logger.debug(f"[Tracer] Failed to send trace event {event}: {e}")
