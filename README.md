
### The Differentiator: Three-Tier AI

When the system encounters a config line it doesn't recognize:

1. **Tier 1 — Regex Matching** (Fast, certain)
   - Known vendor patterns → matched instantly
   
2. **Tier 2 — Embedding Similarity** (Medium speed, high accuracy)
   - Fuzzy matching against known patterns using AI embeddings
   
3. **Tier 3 — LLM Suggestion** (Slow, but human-confirmed)
   - Claude API provides suggestions
   - **Never auto-accepted** — always human review
   - Once confirmed, pattern is saved for future configs

This cascading approach keeps costs low, speed high, and accuracy guaranteed.

---

## Documentation

Start here:

1. **[Team Lecture Notes](docs/team-lecture-notes.md)** — Understanding the problem & solution (read first!)
2. **[System Design Deep Dive](docs/system-design-deep-dive.md)** — Technical architecture & tradeoffs
3. **[Tech Stack Detailed](docs/tech-stack-detailed.md)** — What we build vs. what we present
4. **[Final Implementation Plan](docs/final-implementation-plan.md)** — Day-by-day execution guide
5. **[Architecture Document](docs/ARCHITECTURE.md)** — For judges (2 pages)

---

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_normalization.py -v
```

---

## Adding a New Vendor

No code changes needed! Just add a YAML file:

```bash
# 1. Create vendor patterns file
cat > data/vendor_patterns/my_vendor_patterns.yaml << 'EOF'
remote_access:
  - pattern_name: "ssh_version"
    schema_path: "baseline.remote_access.ssh_version"
    regex: "set ssh version (\\d+)"
    value_type: "int"
  
  - pattern_name: "telnet_disabled"
    schema_path: "baseline.remote_access.telnet_enabled"
    regex: "disable telnet"
    value: false

# ... more patterns ...
EOF

# 2. Done! The system will automatically use these patterns.
```

---

## Adding a New Framework

```bash
# 1. Create framework rules file
cat > data/frameworks/my_framework.yaml << 'EOF'
- id: "MY_1.1"
  name: "SSH Version 2 Enforced"
  schema_path: "baseline.remote_access.ssh_version"
  operator: "=="
  expected_value: 2
  severity: "critical"
  remediation_commands:
    cisco: "ip ssh version 2"
    juniper: "set system services ssh protocol-version v2"

# ... more rules ...
EOF

# 2. Select this framework in the UI or API. Done!
```

---

## API Usage (For Future Integration)

```bash
# Will be available after Day 3 (Phase 2)
# POST /scan with config file
# POST /train to confirm a mapping
# GET /results to fetch compliance findings
```

---

## Demo

### Live Demo (2 minutes)

```bash
# 1. Upload Cisco config → see findings ✓
# 2. Upload unknown vendor config → see unmapped lines
# 3. Train on 2 lines live → re-run → lines now mapped
# 4. Download PDF report with remediation commands
```

See `docs/final-implementation-plan.md` (Section 5.2) for the exact demo script.

---

## Team

Built for **Smart India Hackathon (SIH)** by:
- [Team Lead/Architect Name]
- [AI/NLP Engineer Name]
- [Backend Developer Name]
- [Frontend Developer Name]
- [Research & Presentation Lead Name]

---

## Roadmap

### Phase 1 (MVP — Complete by Demo Day)
- ✓ Single framework (CIS) support
- ✓ 2–3 known vendors (Cisco, Juniper)
- ✓ Human-in-the-loop training loop
- ✓ PDF report generation

### Phase 2 (Production-Ready — Post-SIH)
- Multi-framework support (NIST, STIG, ISO)
- Live device polling via Netmiko/NAPALM
- FastAPI backend for multi-user access
- PostgreSQL for scalability
- Confidence scoring & audit trails

### Phase 3 (Enterprise)
- Kubernetes deployment
- Multi-tenant SaaS model
- CI/CD integration (auto-scan on config change)
- Trend dashboards & compliance drift detection

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Core Language | Python 3.11+ | Netmiko, spaCy, ReportLab all here |
| Normalization | Regex + sentence-transformers + Claude API | Three-tier cascade (cost/latency optimized) |
| Rules Engine | Python + YAML | Data-driven, no code changes to add frameworks |
| Frontend | Streamlit (MVP) → React (Production) | Fast to build, professional enough for demo |
| Database | SQLite (MVP) → PostgreSQL (Production) | Same model, lightweight instance now |
| Reporting | ReportLab | Fine-grained PDF layout control |
| Testing | pytest | Industry standard |

---

## Supported Frameworks

- **CIS Benchmarks** (MVP) — Network device hardening
- **NIST SP 800-53** (Roadmap) — Federal compliance
- **DISA STIG** (Roadmap) — Department of Defense standards
- **ISO/IEC 27001** (Roadmap) — International security management

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

[Specify your license — MIT, Apache 2.0, or see guidelines]

---

## Questions?

Open an issue on GitHub or reach out to the team.

**GitHub Issues:** https://github.com/[YOUR_USERNAME]/netguard-ai/issues

---

**Last Updated:** [Today's Date]
**Status:** SIH Submission (MVP) — In Development
EOF
