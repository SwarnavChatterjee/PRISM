# Architecture Document — NetGuard AI
## For SIH Judges

---

## Page 1: System Overview

### Problem
Modern enterprises have heterogeneous networks (Cisco, Juniper, Palo Alto, etc.) that must comply with security frameworks (CIS, NIST, STIG, ISO). Each vendor uses different CLI syntax, making manual compliance checking slow and error-prone. Existing tools are vendor-locked and require code rewrites for new device types.

### Solution
NetGuard AI is an AI-augmented, vendor-agnostic compliance engine that:
1. **Normalizes** any vendor's config into a canonical schema using a three-tier AI cascade
2. **Evaluates** against chosen compliance framework using data-driven rules
3. **Learns** new vendors automatically through human-in-the-loop training
4. **Reports** findings with exact remediation commands per device

### Architecture Diagram

### Data Flow (One Config File's Journey)

1. **Ingestion:** Raw Juniper config uploaded → vendor guessed as "juniper"
2. **Normalization Tier 1:** Line `set system services ssh root-login deny` → regex matches → maps to `baseline.remote_access.ssh_enabled = false` (confidence 1.0)
3. **Normalization Tier 2:** Unknown line → embedding similarity finds 85% match to known "SSH" pattern → maps with confidence 0.85
4. **Normalization Tier 3:** Truly unknown line → Claude suggests category, human confirms → persisted to `vendor_patterns` table
5. **Compliance:** Normalized config checked against CIS rules → 15 controls evaluated → 12 pass, 3 fail
6. **Reporting:** PDF generated → device ID, findings table, remediation commands → downloaded by user

---

## Page 2: Technical Design

### Key Design Decisions & Tradeoffs

| Decision | Reasoning |
|---|---|
| **Regex-first, LLM-last** | Cost & latency. Regex handles 80%, embeddings handle 15%, LLM only for 5% → lower cost than all-LLM approach |
| **Human-confirmed learning** | Trust. Never auto-commit a pattern without human review → guarantees correctness, prevents hallucination poisoning |
| **Data-driven rules** | Extensibility. Framework rules stored as YAML, not code → adding CIS, NIST, STIG, ISO requires no code change |
| **SQLite for MVP** | Speed to demo. Same schema as PostgreSQL → easy to upgrade later; no multi-user concurrency needed for 5-day sprint |
| **Streamlit for UI** | Fast iteration. Python-native, no separate frontend team needed → working UI in days, not weeks |
| **Static file upload (not live pull)** | Demo reliability. Live SSH adds credential management, network access, vendor-driver complexity → risky on demo day |

### Confidence Scoring

Every normalized field carries a confidence score:
- `1.0` — Exact regex match (certain)
- `0.7–0.9` — Embedding similarity match (high confidence)
- `pending` — LLM suggestion awaiting human confirmation (unconfirmed)

Compliance engine flags low-confidence matches as "needs review" rather than silent pass/fail.

### Explainability & Audit Trail

**Every finding traces back to source:**
```json
{
  "control_id": "CIS_1.1",
  "status": "fail",
  "severity": "critical",
  "source_line": 12,
  "raw_config_line": "no ip ssh version 2",
  "remediation": "ip ssh version 2"
}
```

This satisfies enterprise audit requirements (NFR4).

### Scalability & Roadmap

**MVP (5-day sprint):**
- Single framework (CIS)
- 2–3 known vendors (Cisco, Juniper)
- File upload only
- Single-machine deployment

**Phase 2 (Post-SIH):**
- Multi-framework support via taxonomy mapping
- Live device polling via Netmiko/NAPALM
- FastAPI backend + React frontend
- PostgreSQL database

**Phase 3 (Enterprise):**
- Kubernetes + microservices
- Multi-tenant SaaS model
- Trend dashboards
- CI/CD integration

### Technology Stack

| Layer | MVP | Production |
|---|---|---|
| **Core** | Python 3.11 | Python 3.11+ |
| **Normalization** | regex + sentence-transformers + Claude API | Same, with fine-tuned domain model |
| **Rules** | YAML files + Python evaluator | Same architecture, DB-driven UI |
| **Frontend** | Streamlit | React + MUI |
| **Database** | SQLite | PostgreSQL |
| **Deployment** | Single VM | Kubernetes + load balancer |
| **Reporting** | ReportLab (PDF) | Same + dashboard/API |

---

**Document Version:** 1.0  
**Date:** [Today]  
**Status:** SIH Submission (MVP)  
**Contact:** [Team Lead Email]

