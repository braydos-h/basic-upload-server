# app.py
import os, uuid, time, asyncio, shutil
from pathlib import Path
from datetime import datetime, timedelta

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import aiofiles

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Allow configuration via environment variables
# MAX_SIZE is specified in bytes and defaults to 500 MB
MAX_SIZE = int(os.getenv("MAX_SIZE", 500 * 1024 * 1024))
# TTL_HOURS is the number of hours before a file expires
TTL_HOURS = int(os.getenv("TTL_HOURS", 24))

app = FastAPI(title="500 MB uploader")

# ----- Utility -------------------------------------------------------------
def _file_path(token: str) -> Path:
    return UPLOAD_DIR / token

async def _purge_old_files():
    """Delete everything older than TTL_HOURS."""
    cutoff = time.time() - TTL_HOURS * 3600
    for f in UPLOAD_DIR.iterdir():
        if f.is_file() and f.stat().st_mtime < cutoff:
            try:
                f.unlink()
            except Exception:
                pass

# run cleanup in the background every hour
@app.on_event("startup")
async def schedule_cleanup():
    async def _loop():
        while True:
            await _purge_old_files()
            await asyncio.sleep(3600)   # 1 h
    asyncio.create_task(_loop())

# ----- Routes --------------------------------------------------------------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if file.content_type is None:
        raise HTTPException(400, "Missing content-type header")

    # stream to disk to keep memory usage sane
    token = f"{int(time.time())}_{uuid.uuid4().hex}"
    dest = _file_path(token)
    size = 0

    async with aiofiles.open(dest, "wb") as out:
        while chunk := await file.read(1024 * 1024):  # 1 MB chunks
            size += len(chunk)
            if size > MAX_SIZE:
                await out.close()
                dest.unlink(missing_ok=True)
                limit_mb = MAX_SIZE // (1024 * 1024)
                raise HTTPException(413, f"File too bloody big (limit {limit_mb} MB)")
            await out.write(chunk)

    return {"url": f"/file/{token}", "expires": TTL_HOURS}

@app.get("/file/{token}")
async def serve_file(token: str):
    path = _file_path(token)
    if not path.exists():
        raise HTTPException(404, "File vanished into the void")
    return FileResponse(path, filename=path.name)

# Serve front-end
app.mount("/", StaticFiles(directory="static", html=True), name="static")
