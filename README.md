# Basic Upload Server

A minimal FastAPI application for uploading and sharing files. Uploaded files are stored on disk and cleaned up automatically.

## Environment variables

The behaviour of the server can be tweaked using the following variables:

- `MAX_SIZE` - maximum allowed upload size in **bytes**. Defaults to `524288000` (500 MB).
- `TTL_HOURS` - time in hours before uploaded files are removed. Defaults to `24`.

Example usage:

```bash
MAX_SIZE=104857600 TTL_HOURS=12 uvicorn app:app
```

