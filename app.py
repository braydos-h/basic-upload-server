# app.py
import asyncio
import logging
import time
import uuid
from pathlib import Path

import aiofiles
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_SIZE  = 500 * 1024 * 1024        # 500 MB
TTL_HOURS = 24                       # hours to keep each file

app = FastAPI(title="500 MB uploader")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _file_path(token: str) -> Path:
    """Return the on-disk Path for a given token (token already has extension)."""
    return UPLOAD_DIR / token


async def _purge_old_files() -> None:
    """Delete files older than TTL_HOURS."""
    cutoff = time.time() - TTL_HOURS * 3600
    for f in UPLOAD_DIR.iterdir():
        try:
            if f.is_file() and f.stat().st_mtime < cutoff:
                f.unlink()
        except OSError as exc:
            logger.warning("Failed to delete %s: %s", f, exc)


@app.on_event("startup")
async def _schedule_cleanup() -> None:
    """Run the purge loop in the background every hour."""
    async def _loop():
        while True:
            await _purge_old_files()
            await asyncio.sleep(3600)  # one hour

    asyncio.create_task(_loop())


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if file.content_type is None:
        raise HTTPException(400, "Missing Content-Type header")

    # --- Build safe filename ------------------------------------------------
    ext = Path(file.filename).suffix[:10]  # keeps ".pdf", ".png", "", etc.
    token = f"{int(time.time())}_{uuid.uuid4().hex}{ext}"

    dest = _file_path(token)
    size = 0

    async with aiofiles.open(dest, "wb") as out:
        while chunk := await file.read(1024 * 1024):          # 1 MB chunks
            size += len(chunk)
            if size > MAX_SIZE:
                await out.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(413, "File exceeds 500 MB limit")
            await out.write(chunk)

    return {
        "url":     f"/file/{token}",
        "expires": TTL_HOURS,          # hours until automatic deletion
    }


@app.get("/file/{token}")
async def serve_file(token: str):
    path = _file_path(token)
    if not path.exists():
        raise HTTPException(404, "File vanished into the void")

    return FileResponse(
        path,
        filename=path.name,           # tells browser the correct name+ext
        media_type="application/octet-stream",
    )


# ---------------------------------------------------------------------------
# Static front-end (optional)
# ---------------------------------------------------------------------------

app.mount("/", StaticFiles(directory="static", html=True), name="static")
