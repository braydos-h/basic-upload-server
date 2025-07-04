# cleanup.py
import os, time
from pathlib import Path

UPLOAD_DIR = Path(__file__).parent / "uploads"
TTL_HOURS = 24
cutoff = time.time() - TTL_HOURS * 3600

for f in UPLOAD_DIR.iterdir():
    if f.is_file() and f.stat().st_mtime < cutoff:
        try: f.unlink()
        except: pass
