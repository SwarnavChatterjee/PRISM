# PRISM React frontend

This is the new PRISM web client. It uses React, TypeScript, Vite, and a Node-based development toolchain while keeping the existing Python normalization and compliance engine behind FastAPI.

## Run locally

Use two terminals. In the first terminal, from the repository root, start the API:

```bash
uvicorn api.main:app --reload --port 8000
```

In the second terminal, start the React frontend:

```bash
cd web
npm install
npm run dev
```

If your terminal is already inside `web/`, start the API with:

```bash
uvicorn --app-dir .. api.main:app --reload --port 8000
```

Open `http://localhost:5173`.

During local development, Vite proxies `/api` to `http://localhost:8000`, so the browser does not need direct cross-origin access to the Python API.

## Architecture

```text
React + TypeScript + Vite
              ↓
        FastAPI HTTP API
              ↓
Existing PRISM Python engine + SQLite knowledge store
```

The React client uses the real upload, normalization, training, and compliance endpoints; it does not use placeholder metrics.
