"""Frontend configuration endpoint."""

import os

from fastapi import APIRouter

router = APIRouter(prefix="/api")

DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"


@router.get("/config")
async def get_config():
    """Return frontend configuration flags."""
    return {
        "dev_mode": DEV_MODE,
    }
