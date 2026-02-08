"""Debug trace middleware — only active when DEV_MODE=true."""

import json
import os
import time
from contextvars import ContextVar
from uuid import uuid4

from fastapi import Request

DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

_trace_id: ContextVar[str] = ContextVar("trace_id", default="")
_traces: ContextVar[list] = ContextVar("traces", default=[])


def get_trace_id() -> str:
    return _trace_id.get()


def add_trace(stage: str, data: dict):
    """Add a trace entry for the current request."""
    if not DEV_MODE:
        return
    traces = _traces.get()
    traces.append(
        {
            "stage": stage,
            "timestamp": time.time(),
            "data": data,
        }
    )


async def trace_middleware(request: Request, call_next):
    """Middleware that collects traces and publishes to debug WebSocket."""
    if not DEV_MODE:
        return await call_next(request)

    trace_id = str(uuid4())[:8]
    _trace_id.set(trace_id)
    _traces.set([])

    add_trace(
        "request_start",
        {
            "method": request.method,
            "path": str(request.url.path),
        },
    )

    response = await call_next(request)

    add_trace("request_end", {"status_code": response.status_code})

    traces = _traces.get()
    if traces and hasattr(request.app.state, "redis"):
        await request.app.state.redis.publish(
            "debug_traces", json.dumps({"trace_id": trace_id, "traces": traces})
        )

    return response
