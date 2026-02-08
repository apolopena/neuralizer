"""File upload interception — validate, detect, scrub, publish."""

import json
import logging
import os
from pathlib import Path
from uuid import uuid4

import httpx
import magic
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse

from services.mcp_client import get_mcp_client
from utils.paths import scrub_sandbox

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

SCRUB_FILE_LIMIT = int(os.getenv("SCRUB_FILE_LIMIT_KB", "2048")) * 1024
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://open-webui:8081")

ALLOWED_TYPES = {
    "text/plain",
    "text/csv",
    "text/log",
    "application/json",
    "application/x-ndjson",
}

REJECTED_TYPES = {
    "image/": "Images are not supported. Please paste text content directly.",
    "video/": "Video files are not supported.",
    "audio/": "Audio files are not supported.",
    "application/pdf": "PDF files are not yet supported. Copy and paste the text content instead.",
    "application/zip": "Archive files are not supported. Extract and upload text files.",
}


async def _publish_file_event(
    redis,
    filename: str,
    status: str,
    event_type: str = "file_event",
    content: str = "",
    **extra,
):
    """Publish file event to panel.

    Required fields: {prompt, sanitized, status}
    Extra metadata included for future use.
    """
    payload = {
        # Required by frontend
        "prompt": f"[File Upload: {filename}]",
        "sanitized": content,
        "status": status,
        # Extra metadata
        "type": event_type,
        "filename": filename,
        **extra,
    }
    await redis.publish("prompt_intercept", json.dumps(payload))


async def _proxy_file_to_openwebui(file: UploadFile, content: bytes) -> dict:
    """Proxy file upload to Open WebUI for normal processing."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Reset file position and send to Open WebUI
        files = {"file": (file.filename, content, file.content_type or "text/plain")}
        resp = await client.post(f"{OPENWEBUI_URL}/api/v1/files", files=files)
        return resp.json()


@router.post("/files")
async def intercept_file_upload(request: Request, file: UploadFile = File(...)):
    """Validate file, run detection, scrub if log, publish results.

    When scrubbing is OFF:
    - Non-text files: Rejected with error (always)
    - Text files: Proxied to Open WebUI for normal flow
    """
    redis = request.app.state.redis
    neuralizer = request.app.state.neuralizer
    job_id = str(uuid4())[:8]

    # Sanitize filename
    safe_filename = Path(file.filename).name
    if not safe_filename or safe_filename.startswith("."):
        raise HTTPException(400, "Invalid filename")

    try:
        content = await file.read()

        # 1. Validate size (always, regardless of mode)
        if len(content) > SCRUB_FILE_LIMIT:
            error = (
                f"File too large ({len(content) // 1024} KB). "
                f"Max {SCRUB_FILE_LIMIT // 1024} KB."
            )
            await _publish_file_event(redis, safe_filename, f"Error: {error}")
            raise HTTPException(413, error)

        # 2. Validate MIME
        mime = magic.from_buffer(content[:2048], mime=True)
        for prefix, msg in REJECTED_TYPES.items():
            if mime.startswith(prefix) or mime == prefix:
                await _publish_file_event(redis, safe_filename, f"Error: {msg}")
                raise HTTPException(415, msg)

        if mime not in ALLOWED_TYPES and not mime.startswith("text/"):
            error = f"Unsupported file type: {mime}"
            await _publish_file_event(redis, safe_filename, f"Error: {error}")
            raise HTTPException(415, error)

        # 3. Check scrubbing mode — if OFF, proxy text files to Open WebUI
        if not request.app.state.scrubbing_enabled:
            return await _proxy_file_to_openwebui(file, content)

        # 4. Decode
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            error = "File does not appear to be valid text."
            await _publish_file_event(redis, safe_filename, f"Error: {error}")
            raise HTTPException(415, error)

        # 5. Neuralizer detection (peek at sample to determine category)
        detection = await neuralizer.detect(text[:4096])
        category = detection.get("category", "")

        # Fail-closed: detection errors block the upload
        if category == "error":
            error_msg = detection.get("summary", "Detection failed")
            await _publish_file_event(redis, safe_filename, f"Error: {error_msg}")
            raise HTTPException(
                503, f"Detection failed: {error_msg}. Upload blocked for safety."
            )

        # 6. Determine scrub patterns based on category
        # For log files: use ALL log + standard patterns (union)
        # For other text: use ALL standard patterns
        # Detection sample determines category, but we scrub entire file with all patterns
        is_log = category == "log_file"

        if not detection.get("needs_sanitization", False):
            # Clean file — return fake success to Open WebUI
            await _publish_file_event(
                redis, safe_filename, "🛡️ Clean — no sensitive content detected"
            )
            return _fake_openwebui_response(job_id, safe_filename, "clean")

        # 7. Save input file
        input_filename = f"{job_id}.txt"
        output_filename = f"{job_id}_{safe_filename}"
        in_path = scrub_sandbox.resolve(input_filename, "in")
        in_path.parent.mkdir(parents=True, exist_ok=True)
        in_path.write_text(text)

        # 8. Scrub file via MCP
        # Log files: ALL log + standard patterns (catches emails, API keys in logs)
        # Other text files: ALL standard patterns
        mcp = await get_mcp_client()
        if is_log:
            all_patterns = [
                "ip",
                "private_ip",
                "internal_url",
                "timestamp",
                "endpoint",
                "user",  # log
                "email",
                "phone",
                "name",
                "api_key",
                "secret",
                "bearer",
                "path",
                "resource_id",  # standard
            ]
        else:
            all_patterns = [
                "email",
                "phone",
                "name",
                "api_key",
                "secret",
                "bearer",
                "path",
                "resource_id",
            ]
        summary = await mcp.scrub_log_as_file(
            input_filename, output_filename, all_patterns
        )

        # 9. Publish to panel
        items_scrubbed = summary.get("items_scrubbed", 0)
        lines_processed = summary.get("lines_processed", 0)
        type_summary = summary.get("summary", {})
        breakdown = (
            ", ".join(f"{k}: {v}" for k, v in type_summary.items())
            if type_summary
            else ""
        )
        status_msg = f"🛡️ {category.replace('_', ' ').title()} — {items_scrubbed} items scrubbed in {lines_processed} lines"
        if breakdown:
            status_msg += f" ({breakdown})"
        status_msg += f"\nDownload: /api/v1/files/download/{job_id}"
        await _publish_file_event(
            redis,
            safe_filename,
            status_msg,
            event_type="file_scrubbed",
            job_id=job_id,
            category=category,
            summary=summary,
            download_url=f"/api/v1/files/download/{job_id}",
        )

        # 10. Return fake success to Open WebUI (no RAG processing)
        return _fake_openwebui_response(job_id, safe_filename, "scrubbed")

    except HTTPException:
        raise
    except Exception as e:
        error = f"Unexpected error: {e!s}"
        await _publish_file_event(redis, safe_filename, f"Error: {error}")
        raise HTTPException(500, error)


def _fake_openwebui_response(job_id: str, filename: str, status: str) -> dict:
    """Return response that makes Open WebUI not process the file for RAG.

    COMPATIBILITY NOTE: Based on Open WebUI v0.5.x API. Schema changes may require updates.
    See integration test test_openwebui_schema for validation.
    """
    return {
        "status": True,
        "id": f"neuralizer-{job_id}",
        "filename": filename,
        "data": {"status": "completed", "content": ""},  # Empty = no RAG
        "meta": {"name": filename, "content_type": "text/plain", "size": 0},
    }


@router.get("/files/download/{job_id}")
async def download_scrubbed_file(job_id: str):
    """Download a scrubbed file by job ID.

    SECURITY NOTE: Unauthenticated by design — assumes localhost-only access.
    This is a local development tool, not exposed to public internet.
    """
    out_dir = scrub_sandbox.root / "out"

    matches = list(out_dir.glob(f"{job_id}_*"))
    if not matches:
        raise HTTPException(404, f"No scrubbed file found for job {job_id}")

    file_path = matches[0]
    original_filename = file_path.name[len(job_id) + 1 :]

    # Sanitize filename for Content-Disposition header (remove quotes, newlines)
    safe_download_name = (
        original_filename.replace('"', "").replace("\n", "").replace("\r", "")
    )

    def iter_file():
        with open(file_path, "rb") as f:
            yield from f

    return StreamingResponse(
        iter_file(),
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="scrubbed_{safe_download_name}"'
        },
    )
