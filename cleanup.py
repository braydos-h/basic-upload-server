# cleanup.py
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(__file__).parent / "uploads"
TTL_HOURS = 24
cutoff = time.time() - TTL_HOURS * 3600

for f in UPLOAD_DIR.iterdir():
    if f.is_file() and f.stat().st_mtime < cutoff:
        try:
            f.unlink()
        except OSError as exc:
            logger.warning("Failed to delete %s: %s", f, exc)
