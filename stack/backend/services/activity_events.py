"""Agent activity event models with Pydantic validation."""

from datetime import datetime
from typing import Any, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


class AgentEvent(BaseModel):
    """Validated agent activity event."""

    # Mandatory fields
    agent: str = Field(..., description="Agent name")
    session_id: str = Field(..., description="Session identifier for event correlation")
    model: str = Field(..., description="Model used for this operation")
    state: str = Field(..., description="Event state (start, complete, error, custom)")
    timestamp: datetime = Field(..., description="Event timestamp in UTC")

    # Optional validated fields
    duration_ms: Optional[int] = Field(None, ge=0)
    output: Optional[str] = Field(None, description="Agent output text")
    thinking: Optional[Union[bool, str]] = Field(None)
    temperature: Optional[float] = Field(None, ge=0, le=2)
    error: Optional[str] = Field(None, description="Error message")
    provider: Optional[str] = Field(None, description="Provider name")

    # Generic payload for custom/agent-specific fields
    data: Optional[dict[str, Any]] = Field(None)

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )
