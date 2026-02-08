"""Frontend configuration endpoint."""

import os

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import Response

router = APIRouter(prefix="/api")

DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"
OPENWEBUI_INTERNAL_URL = os.getenv("OPENWEBUI_INTERNAL_URL", "http://open-webui:8081")


@router.get("/config")
async def get_config():
    """Return frontend configuration flags."""
    return {
        "dev_mode": DEV_MODE,
    }


# CSS applied in both modes
BASE_CSS = """
/* Hide suggestions section below input */
.mx-auto.max-w-2xl.font-primary.mt-2 {
  display: none !important;
}

/* Replace model header with NeurALIzer branding */
.flex.flex-row.justify-center.gap-3 {
  align-items: center !important;
  gap: 0 !important;
}

/* Hide original model button and shrink container */
button[aria-label^="Get information on"] {
  display: none !important;
}
.flex.flex-row.justify-center.gap-3 > div:first-child {
  display: none !important;
}

/* Add N icon to left of "Private LLM" text */
.flex.flex-row.justify-center.gap-3::before {
  content: '';
  display: block;
  width: 40px;
  height: 40px;
  background-image: url("/neuralizer-icon.svg");
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  flex-shrink: 0;
  margin-right: 8px;
}

/* Add full NeurALIzer logo at top of page */
body::before {
  content: '';
  display: block;
  width: 100%;
  height: 100px;
  background-image: url("/neuralizer-logo-100h-transparent.png");
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  margin-bottom: 1rem;
}

/* Replace model name with "Private LLM" */
.text-3xl span.line-clamp-1 {
  font-size: 0 !important;
}
.text-3xl span.line-clamp-1::after {
  content: 'Private LLM';
  font-size: 1.875rem !important;
}

/* + button menu: hide Capture, Attach Notes, Attach Knowledge (keep Upload Files, Attach Webpage) */
[data-melt-dropdown-menu] .w-full:nth-child(2),
[data-melt-dropdown-menu] .w-full:nth-child(4),
[data-melt-dropdown-menu] .w-full:nth-child(5) {
  display: none !important;
}

/* Change "Upload Files" to "Upload Plaintext File" */
[data-melt-dropdown-menu] .w-full:first-child .line-clamp-1 {
  font-size: 0 !important;
}
[data-melt-dropdown-menu] .w-full:first-child .line-clamp-1::after {
  content: 'Upload Plaintext File';
  font-size: 0.875rem !important;
}

/* Replace model name in chat messages with "Local LLM" */
#response-message-model-name {
  font-size: 0 !important;
}
#response-message-model-name::after {
  content: 'Local LLM';
  font-size: 0.875rem !important;
}

"""

# Additional CSS when scrubbing is enabled
SCRUB_MODE_CSS = """
/* Scrub mode: cyan text to confirm mode is active */
* {
  color: #22d3ee !important;
}

/* Hide OWU chrome - sidebar and top bar */
.flex.items-center.w-full.max-w-full,
#sidebar,
[data-sidebar],
.sidebar,
nav[class*="sidebar"],
div[class*="sidebar"] {
  display: none !important;
}

/* Hide integrations button, voice input, voice mode, note button - keep + button */
#integration-menu-button,
#voice-input-button,
button[aria-label="Voice mode"],
.bg-gray-200\\/50.dark\\:bg-gray-800\\/50,
#send-message-button:not([type="submit"]) {
  display: none !important;
}

/* Left justify and tighter gap for logo + text */
.flex.flex-row.justify-center.gap-3 {
  justify-content: flex-start !important;
  padding-left: 1rem;
}

/* Replace placeholder with PII hint */
#chat-input p[data-placeholder]::before {
  content: 'Input will be analyzed for Personally Identifiable Information' !important;
}
"""


@router.get("/owu-styles")
async def owu_styles(request: Request):
    """Return dynamic CSS for Open WebUI based on scrubbing mode."""
    scrubbing = getattr(request.app.state, "scrubbing_enabled", True)

    css = BASE_CSS
    if scrubbing:
        css += SCRUB_MODE_CSS

    return Response(
        content=css,
        media_type="text/css",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )


@router.get("/health/openwebui")
async def openwebui_health():
    """Check Open WebUI health status with granular reporting."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{OPENWEBUI_INTERNAL_URL}/api/version")
            if resp.status_code == 200:
                return {"status": "ready", "message": "Open WebUI is ready"}
            else:
                return {
                    "status": "starting",
                    "message": "Open WebUI is responding but not fully ready",
                }
    except httpx.ConnectError:
        return {"status": "starting", "message": "Loading local inference"}
    except httpx.TimeoutException:
        return {"status": "initializing", "message": "Database migrations in progress"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
