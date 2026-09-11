# PRISM Architecture

PRISM is a local network-configuration compliance scanner. The current implementation accepts uploaded text configurations, detects Cisco or Juniper syntax, normalizes known lines into a small canonical baseline, and evaluates that baseline against YAML-defined CIS controls.

## Runtime flow

```text
Configuration file
        |
        v
FastAPI upload endpoint
        |
        v
Vendor detection + YAML regex normalization
        |
        v
Canonical baseline + unmapped source lines
        |
        v
CIS benchmark evaluator
        |
        v
Compliance JSON returned to the React dashboard
        |
        v
Deterministic PDF report export
```

The frontend is intentionally separate from the engine. It communicates through the existing FastAPI endpoints and does not contain a second parser or a second data source.

## Main components

| Component | Responsibility |
|---|---|
| `api/main.py` | Upload and training HTTP endpoints, CORS, application wiring |
| `src/ingestion` | Validate supported text uploads and read their contents |
| `src/normalization` | Detect vendors and map known lines using YAML regex patterns |
| `src/schema` | Define the canonical baseline model and provenance metadata |
| `src/compliance` | Load framework YAML and produce pass/fail findings |
| `src/training` | Persist human-confirmed mappings and re-run normalization |
| `src/storage` | Initialize and access the local SQLite knowledge store |
| `web/src` | React/TypeScript dashboard for upload, analysis, findings, and training |

## Data and trust boundaries

- Framework rules live in `data/frameworks/cis_benchmarks.yaml`.
- Vendor patterns live in `data/vendor_patterns/`.
- Demo inputs are plain text files under `data/sample_configs/`.
- The API returns source-line references, confidence, provenance, and remediation commands with each analysis.
- Unknown lines remain unmapped until a user explicitly confirms a training mapping.
- The local SQLite database is runtime state and is ignored by Git.

## Current scope

The implementation is deterministic and local. It does not currently include live device polling, embedding similarity, or an LLM fallback. PDF generation is available through the reporting package and `/api/report/pdf`.

## Development commands

```bash
pytest -q
uvicorn api.main:app --reload --port 8000
cd web && npm install && npm run dev
```
