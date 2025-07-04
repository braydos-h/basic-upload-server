# Basic Upload Server

This is a minimal FastAPI application that accepts large file uploads (up to 500 MB) and serves them back via a generated download link. Old uploads are automatically cleaned up.

## Requirements

Install dependencies with `pip`:

```bash
pip install -r requirements.txt
```

## Running

Launch the server with `uvicorn`:

```bash
uvicorn app:app --reload
```

The frontend is available at `http://localhost:8000/` after starting the server.

