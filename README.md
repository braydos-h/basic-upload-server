# Basic Upload Server

This project provides a lightweight FastAPI application that lets users upload files up to 500&nbsp;MB and then retrieve them via a download link. Old uploads are automatically removed after 24&nbsp;hours to conserve disk space.

## Setup

Install the Python dependencies using `pip`:

```bash
pip install -r requirements.txt
```

## Running the server

Start the development server with auto-reload enabled:

```bash
uvicorn app:app --reload
```

Visit `http://localhost:8000` in your browser and use the simple web interface to upload a file. The server returns a link where the file can be downloaded until it expires.

## Cleaning up

To manually remove files older than 24&nbsp;hours, run:

```bash
python cleanup.py
```

Uploads are also cleaned automatically by the FastAPI application when it is running.

## License

No license file is provided with this repository.
