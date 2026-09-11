# PRISM

PRISM is a vendor-aware network configuration compliance scanner. It turns Cisco and Juniper configuration text into a canonical baseline, evaluates that baseline against CIS benchmark rules, and shows source-line findings with remediation guidance.

The repository contains the working deterministic engine and React dashboard. It does not include the old Streamlit client, placeholder runtime data, live device polling, or an AI/LLM fallback.

## What is included

- FastAPI API for configuration upload, analysis, and human-confirmed training.
- YAML-driven Cisco and Juniper normalization patterns.
- CIS benchmark controls with source references and remediation commands.
- SQLite-backed training mappings.
- React/TypeScript/Vite frontend using the real API.
- Deterministic PDF compliance reports with source-line findings and remediation.
- Plain-text demo configurations, including compliant, noncompliant, and faulty examples.

## Quick start

Requirements: Python 3.11+, Node.js, and npm.

```bash
git clone https://github.com/SwarnavChatterjee/PRISM.git
cd PRISM

python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt

# Terminal 1: API
uvicorn api.main:app --reload --port 8000

# Terminal 2: frontend
cd web
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite development server proxies `/api` requests to `http://localhost:8000`.

## API

The current API exposes:

- `GET /health` — health check.
- `POST /api/analyze` — upload a configuration and return normalized data plus compliance findings.
- `POST /api/train` — confirm a mapping for an unmapped line and re-run analysis.
- `POST /api/report/pdf` — render a completed analysis as a downloadable PDF report.

The API accepts text configuration files. The frontend accepts `.cfg`, `.conf`, `.config`, `.set`, `.txt`, and `.log` files.

## Demo files

The supported demo inputs are in [data/sample_configs](data/sample_configs):

- `cisco_compliant.txt`
- `cisco_noncompliant.txt`
- `cisco_faulty_demo.txt`
- `juniper_compliant.txt`
- `juniper_noncompliant.txt`
- `unknown_vendor.txt`

These are demonstration inputs only. They are not loaded automatically and do not seed fake dashboard metrics.

## Architecture

```text
Text config
    -> FastAPI upload
    -> vendor detection
    -> YAML regex normalization
    -> canonical baseline + unmapped lines
    -> CIS evaluator
    -> React dashboard
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for component responsibilities and current boundaries.

## Repository layout

```text
api/                       FastAPI application
data/frameworks/           CIS benchmark definitions
data/sample_configs/       Plain-text demo inputs
data/vendor_patterns/      Cisco and Juniper regex mappings
database/                  SQLite schema
src/ingestion/             Upload validation
src/normalization/         Vendor detection and normalization
src/schema/                Canonical baseline models
src/compliance/            Framework evaluation
src/storage/               SQLite helpers
src/training/              Human-confirmed mappings
tests/                     Python unit tests and expected results
web/src/                   React frontend
```

## Verification

Run the backend tests:

```bash
pytest -q
```

Build the frontend:

```bash
cd web
npm run build
```

## Current limitations

Normalization and PDF reporting are intentionally deterministic and pattern-based. Unknown lines are surfaced for review and training; they are not guessed by an external model. Live SSH collection, semantic matching, and multi-framework execution are not part of this version.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [CIS control catalog](docs/cis-control-catalog.md)
- [Demo data guide](docs/demo-data-guide.md)
- [Schema review](docs/schema-review.md)
- [Team member handoff](docs/team-member-2-handoff.md)
- [Contributing](CONTRIBUTING.md)
