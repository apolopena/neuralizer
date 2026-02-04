"""Agent activity monitoring with automatic timing and Redis pub/sub."""

import time
import json
import logging
from datetime import datetime, timezone
from typing import Any

from redis.asyncio import Redis

from services.activity_events import AgentEvent

logger = logging.getLogger(__name__)

AGENT_ACTIVITY_CHANNEL = "agent_activity"


class AgentActivityMonitor:
    """Centralized agent activity monitoring with automatic timing.

    Timing state machine:
    - 'X_start' -> starts timer for state X
    - 'X_complete' -> calculates duration, adds duration_ms
    - 'X_error' -> calculates duration, adds duration_ms
    """

    def __init__(self, redis: Redis, enabled: bool = True):
        self.redis = redis
        self.enabled = enabled
        self.channel = AGENT_ACTIVITY_CHANNEL
        self._timers: dict[str, float] = {}
        logger.info(f"AgentActivityMonitor initialized (enabled={enabled})")

    async def publish(
        self, agent: str, session_id: str, model: str, state: str, **data: Any
    ) -> None:
        """Publish an agent activity event with automatic timing."""
        if not self.enabled:
            return

        # Handle timing state machine
        duration_ms = None
        if state.endswith("_start"):
            state_base = state[:-6]
            timer_key = f"{agent}:{session_id}:{state_base}"
            self._timers[timer_key] = time.monotonic()

        elif state.endswith("_complete") or state.endswith("_error"):
            suffix_len = 9 if state.endswith("_complete") else 6
            state_base = state[:-suffix_len]
            timer_key = f"{agent}:{session_id}:{state_base}"

            if timer_key in self._timers:
                start_time = self._timers.pop(timer_key)
                duration_ms = int((time.monotonic() - start_time) * 1000)
                data["duration_ms"] = duration_ms

        # Create validated event
        try:
            event = AgentEvent(
                agent=agent,
                session_id=session_id,
                model=model,
                state=state,
                timestamp=datetime.now(timezone.utc),
                **data,
            )
        except Exception as e:
            logger.error(f"Failed to create AgentEvent: {e}")
            return

        # Publish to Redis
        try:
            message = {
                "state": event.state,
                "agent": event.agent,
                "session_id": event.session_id,
                "model": event.model,
                "timestamp": event.timestamp.isoformat(),
                "data": {},
            }

            if event.duration_ms is not None:
                message["data"]["duration_ms"] = event.duration_ms
            if event.output is not None:
                message["data"]["output"] = event.output
            if event.thinking is not None:
                message["data"]["thinking"] = event.thinking
            if event.temperature is not None:
                message["data"]["temperature"] = event.temperature
            if event.provider is not None:
                message["data"]["provider"] = event.provider
            if event.error is not None:
                message["data"]["error"] = event.error
            if event.data is not None:
                message["data"].update(event.data)

            await self.redis.publish(self.channel, json.dumps(message))
            logger.debug(f"Published {state} event for {agent} (session {session_id})")

        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
