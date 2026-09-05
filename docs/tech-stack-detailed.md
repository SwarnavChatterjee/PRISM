# Detailed Tech Stack
### Two Versions: What We Actually BUILD (5-day MVP) vs. What We PRESENT (Full Product Vision)

*Read this alongside the earlier system design doc. Every layer below lists: what we build for real, what we claim in the PPT as the full-product architecture, and why the gap between them is justified (this is what you say if a judge asks "does this actually run at that scale?").*

---

## 0. The Governing Principle
Every technology chosen for the MVP must be a **real, working subset** of the technology named in the full-product vision — never a fake stand-in. e.g., SQLite (MVP) is a legitimate smaller sibling of PostgreSQL (full product) — same relational model, same SQL, just lighter. This means when a judge asks "you said Postgres/Kubernetes/etc. in the slide, but I see SQLite in the code" — the honest answer is "yes, MVP uses the lightweight version of the same architecture; the code is structured to swap in the production version without a rewrite." That's a strength, not a lie, if you frame it that way.

---

## 1. Ingestion Layer

| | MVP (Build) | Full Product Vision (PPT) |
|---|---|---|
| Primary method | Manual file upload (.txt/.cfg), single or bulk (zip) | Same, **plus** scheduled live polling |
| Live device connection | Not built; mentioned as roadmap | **Netmiko** (broad multi-vendor SSH driver support — Cisco, Juniper, Arista, Huawei, Fortinet, etc.) and **NAPALM** for vendors with normalized "getters" |
| Cloud-native sources | Not built | AWS/Azure/GCP APIs (Security Group / NSG configs pulled via `boto3` / `azure-mgmt-network` SDKs) |
| File formats supported | Plain text CLI dumps | + JSON/XML exports, NETCONF/YANG-modeled configs for newer devices |

**Why Netmiko over NAPALM for the core collection layer:** Netmiko supports a much longer list of vendors (100+) because it just wraps SSH/Telnet sessions and lets you send raw CLI commands — exactly what we need since our own AI does the normalization. NAPALM pre-normalizes some data for its ~15 supported platforms, which would compete with our own normalization story rather than complement it.

---

## 2. Normalization Engine (Core AI/NLP Layer)

This is the layer most worth being detailed and precise about — it's your technical differentiator.

| Tier | MVP (Build) | Full Product Vision (PPT) |
|---|---|---|
| Tier 1 — Exact/rule match | Python `re` (regex) + hand-written pattern library per known vendor, stored as YAML | Same core approach, scaled to a much larger auto-curated pattern library across all onboarded vendors |
| Tier 2 — Fuzzy/semantic match | `sentence-transformers` (e.g. `all-MiniLM-L6-v2` model) for embedding generation + cosine similarity against known-pattern embeddings | Same, potentially upgraded to a fine-tuned domain-specific embedding model trained on network config corpora |
| Tier 3 — Novel-pattern suggestion | **Anthropic Claude API** (few-shot prompt: "here are 5 examples of config-line → category mappings, classify this new line") — used sparingly, output always shown to human for confirmation, never auto-committed | Same architecture, at production scale with caching, batching, and possibly a fine-tuned smaller model to cut cost/latency once enough labeled data exists |
| Libraries | `spacy` (optional, for tokenization/POS tagging if doing rule generalization from labeled examples), `scikit-learn` (for any lightweight classifier over embeddings) | Same + potential move to a proper ML pipeline (`MLflow` for experiment tracking, model versioning) |

**Key technical detail worth stating in the PPT:** the three tiers form a **cost/latency/accuracy cascade** — cheapest and fastest first, most expensive and slowest last, and the expensive tier is *only* invoked on the small fraction of lines that fail the first two. This is the concrete answer to "why not just use an LLM for everything" (cost + latency + hallucination risk).

---

## 3. Canonical Schema / Knowledge Representation

| | MVP (Build) | Full Product Vision (PPT) |
|---|---|---|
| Format | JSON (Security Baseline Model, as designed earlier) | Same, formalized as a **JSON Schema** with strict validation, versioned as the product evolves |
| Storage of schema itself | Static Python dict / JSON file | Schema registry (versioned, e.g. stored in a dedicated `schema_versions` table so old scans remain interpretable even as the schema grows) |

---

## 4. Compliance Engine

| | MVP (Build) | Full Product Vision (PPT) |
|---|---|---|
| Rule storage | YAML files per framework (`cis_rules.yaml`, etc.) | Same approach, stored in DB (`framework_rules` table) with an admin UI to add/edit rules without touching files at all |
| Rule evaluation | Custom lightweight Python evaluator (walk the YAML, apply operator, compare to normalized JSON) | Same logic, potentially wrapped as a proper rules engine (e.g. **JSON Logic** or **Durable Rules**) if rule complexity grows (AND/OR conditions across multiple fields) |
| Frameworks covered (real, working) | CIS only | CIS + NIST SP 800-53 + DISA STIG + ISO/IEC 27001 (via the shared taxonomy-mapping approach described in the system design doc) |

---

## 5. Training Loop (Human-in-the-Loop System)

| | MVP (Build) | Full Product Vision (PPT) |
|---|---|---|
| Interface | Built directly into the Streamlit app — a simple form: raw line + dropdown of categories + submit | Dedicated low-code labeling UI (could still be Streamlit-based, or a React component) with richer context (surrounding lines, vendor documentation lookup suggestions, confidence-scored auto-suggestions) |
| Persistence of learned mappings | SQLite table `vendor_patterns(vendor, raw_pattern, schema_path, confidence, created_by, created_at)` | Same table structure in PostgreSQL, versioned, with an audit trail and possibly a review/approval workflow for enterprise deployments (a senior admin approves a junior admin's new mapping before it's trusted org-wide) |

---

## 6. Backend / Application Layer

| | MVP (Build) | Full Product Vision (PPT) |
|---|---|---|
| Language | Python | Python (core AI/compliance logic stays Python regardless of scale — this is a genuine, defensible constant) |
| API framework | Not strictly needed if using Streamlit directly calling Python functions | **FastAPI** — async, auto-generated OpenAPI docs, natural fit if the frontend becomes a separate React app or if third-party integrations are needed (e.g., a CI/CD pipeline calling the compliance engine via API) |
| Task handling | Synchronous, in-process (fine for single-file, single-user demo) | Background task queue — **Celery** with **Redis** as broker, for bulk scans across hundreds of devices without blocking the UI |

---

## 7. Frontend / Dashboard

| | MVP (Build) | Full Product Vision (PPT) |
|---|---|---|
| Framework | **Streamlit** — fastest path to a working multi-screen Python-native UI for a 5-day build | **React** (with a component library like MUI or shadcn/ui) for a polished, production-grade multi-user dashboard; Streamlit mentioned as "what we validated the UX with" |
| Screens | Upload → Processing status → Training interface → Results/Report download (4 screens) | Same 4 core flows, plus: multi-device fleet view, compliance trend/drift dashboard over time, user/role management, framework/rule management console |
| Charting (for trend views) | Not built in MVP | **Recharts** or **Chart.js** for compliance-over-time visualizations |

---

## 8. Data Collection Libraries (Detail)

| Library | Purpose | MVP or Full? |
|---|---|---|
| **Netmiko** | Multi-vendor SSH session handling, sending CLI commands, retrieving raw config text | Full product (live pull); MVP just parses uploaded text files, so Netmiko is mentioned as roadmap unless a stretch goal is reached |
| **NAPALM** | Higher-level "getters" for a subset of vendors (useful for schema-design inspiration even if not directly used) | Reference/inspiration only |
| **Paramiko** | Underlying SSH library that Netmiko itself is built on — worth knowing about if Netmiko doesn't support a specific unusual device and a raw SSH session is needed | Full product, fallback case |

---

## 9. Reporting Engine

| | MVP (Build) | Full Product Vision (PPT) |
|---|---|---|
| PDF generation | **ReportLab** — fine-grained control over layout (title page, color-coded severity table, remediation appendix) | Same core library; templated per-organization branding (logo, color scheme) as a customer-facing feature |
| Alternative considered | FPDF2 — simpler API but weaker layout control for tables/styling | Not chosen — ReportLab's flexibility is worth the slightly steeper learning curve |

---

## 10. Database / Storage

| | MVP (Build) | Full Product Vision (PPT) |
|---|---|---|
| Database | **SQLite** — zero setup, file-based, perfectly sufficient for a single-machine demo | **PostgreSQL** — proper concurrent multi-user access, JSONB columns for storing the normalized Security Baseline Model natively, mature tooling |
| Schema | `devices`, `scan_results`, `vendor_patterns`, `framework_rules`, `audit_log` | Same tables, normalized further for multi-tenancy (`organizations`, `users`, `roles`) |
| File storage (raw configs, generated PDFs) | Local filesystem | Cloud object storage — **AWS S3** / **Azure Blob Storage**, with lifecycle policies for retention/audit compliance |

---

## 11. AI/ML Supporting Libraries (Detail)

| Library | Purpose |
|---|---|
| `sentence-transformers` | Generate embeddings for the Tier-2 fuzzy-matching step |
| `scikit-learn` | Cosine similarity computation, any lightweight classification if needed |
| `spacy` | Optional — tokenization, part-of-speech tagging if building more sophisticated pattern generalization from labeled training examples |
| `anthropic` (Python SDK) | Calling Claude for Tier-3 novel-pattern suggestions |
| `pandas` | Data wrangling for bulk scan results, generating summary statistics for reports/dashboards |

---

## 12. DevOps / Deployment

| | MVP (Build) | Full Product Vision (PPT) |
|---|---|---|
| Hosting | Local machine / single cloud VM for the demo | Containerized (**Docker**) services orchestrated with **Kubernetes** for horizontal scaling across many concurrent scans |
| CI/CD | Manual git push | **GitHub Actions** — automated testing, linting, and deployment pipeline |
| Monitoring | Not built | **Prometheus + Grafana** for system health; structured logging for the audit trail requirement |
| Secrets management | `.env` file, not committed to git | **AWS Secrets Manager** / **HashiCorp Vault** for device credentials used in live polling |

---

## 13. Testing

| | MVP (Build) | Full Product Vision (PPT) |
|---|---|---|
| Unit tests | `pytest` for normalization pattern matching and compliance rule evaluation logic (at least core paths) | Same framework, full coverage + integration tests + a labeled "golden dataset" of sample configs across vendors for regression testing normalization accuracy over time |

---

## 14. Consolidated Stack Summary (for a PPT slide)

**Core Language:** Python 3.11+

**AI/NLP:** sentence-transformers (embeddings) → scikit-learn (similarity) → Anthropic Claude API (novel-pattern fallback, human-confirmed)

**Data Collection:** Netmiko (multi-vendor SSH) + NAPALM (reference) + cloud SDKs (`boto3`, Azure SDK) for cloud-native security groups

**Backend:** FastAPI (production) / direct Python functions (MVP)

**Frontend:** Streamlit (MVP) → React + MUI (production)

**Database:** SQLite (MVP) → PostgreSQL (production), with S3/Blob Storage for raw files and reports

**Compliance Rules Engine:** Custom YAML-driven rule evaluator (both MVP and production — this doesn't need to change with scale)

**Reporting:** ReportLab (PDF generation)

**DevOps:** Docker + Kubernetes + GitHub Actions + Prometheus/Grafana (production)

---

## 15. One Sentence to Say If Asked "Is This Really What You Built?"
**"The architecture is identical at every scale — we built the lightweight version of every layer (SQLite instead of Postgres, Streamlit instead of React, single-machine instead of Kubernetes) so the exact same code and logic can be pointed at production infrastructure without a redesign — we're demoing the engine, not a mockup of it."**
