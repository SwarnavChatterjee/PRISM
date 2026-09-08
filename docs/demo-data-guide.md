# Demo Data Guide — PRISM

This is the walkthrough script for using the fixtures in
`data/sample_configs/` to run PRISM's core demo narrative: **upload →
normalize → check compliance → train on the unknown → re-check →
report.** Pair this with `docs/cis-control-catalog.md` for control
definitions and `data/sample_configs/README.md` for per-file technical
detail.

## Recommended demo order

### 1. Compliance, proven (Cisco)
Upload `data/sample_configs/cisco_compliant.txt`.
- **Shows:** all 10 live CIS MVP controls (CIS-1.1–1.10) passing, with
  source-line citations in the provenance output.
- **Talking point:** "every pass/fail traces back to the exact config
  line — this isn't a black box."

### 2. Failure detection (Cisco)
Upload `data/sample_configs/cisco_noncompliant.txt`.
- **Shows:** 6 of the 10 live controls failing (SSHv1, Telnet
  permitted, HTTP server on, no AAA, no password encryption, no
  syslog), each with the specific offending line and the Cisco
  remediation command from the catalog.
- **Talking point:** "we don't just say fail — we hand the admin the
  exact fix command."

### 3. Cross-vendor proof (Juniper)
Upload `data/sample_configs/juniper_compliant.txt` and
`juniper_noncompliant.txt`.
- **Shows:** the same taxonomy of controls evaluated against
  completely different config syntax, including three controls
  correctly marked "not applicable" for Juniper (password-encryption,
  CDP, RSA modulus) rather than wrongly failed.
- **Talking point:** "this is the vendor-agnostic claim proven, not
  just asserted — same rule taxonomy, two unrelated syntaxes, correct
  N/A handling where a control genuinely doesn't apply."

### 4. The differentiator: training loop on a vendor never seen before
Upload `data/sample_configs/unknown_vendor.txt` (fictional "NexaOS"
syntax, invented for this fixture only).
- **Shows:** 7 security-relevant lines flagged `needs_training`
  instead of being silently dropped or guessed at — this is NFR3
  (graceful degradation) proven live.
- **Live-train** 2–3 lines (recommended: `zone-policy default`,
  `admin-access secure-shell`, `audit-stream` — see
  `data/sample_configs/README.md` for the exact mappings).
- **Re-run normalization** and show the previously-unmapped lines are
  now understood, with a partial compliance verdict available on the
  newly-mapped fields.
- **Talking point:** "the system just got smarter, live, in front of
  you — and it never needed to guess. It asked."

### 5. Reporting
Generate the PDF report from any of the above runs.
- **Shows:** findings, severity, and remediation commands rendered for
  a security team to hand to a manager.

**Total demo time target:** under 90 seconds for steps 1, 4, and 5 if
running the tight version; use steps 2–3 as backup/Q&A material if time
allows.

---

## Honest MVP limitations (state these proactively, don't wait to be asked)

- **No live SSH collection.** Every fixture here is a static file
  upload. Live device pull via Netmiko is Phase 2 roadmap, not
  implemented.
- **CIS-only for the live compliance engine.** NIST SP 800-53, DISA
  STIG, and ISO 27001 mappings are Phase 1/2 roadmap items; only the
  CIS taxonomy is wired into `src/compliance/engine.py` today.
- **Six controls (CIS-2.1–2.6) are researched and documented but not
  yet evaluated automatically** — they require a schema extension that
  hasn't been approved yet (see `docs/schema-review.md`). Don't claim
  these are "checked" in the demo; say "researched and ready, pending
  a schema change."
- **No production-scale or multi-tenant deployment.** This is a
  single-process, SQLite-backed MVP intended for a demo laptop, not a
  production compliance platform.
- **The LLM-assisted (Tier 3) normalization tier is a suggestion
  engine only, and always requires human confirmation before it's
  persisted** — never auto-accepted. If Tier 3 is too slow/unreliable
  on demo day, fall back to Tier 1 (regex) + Tier 2 (embedding) only
  and explain Tier 3 verbally rather than risk a live API timeout.
- **All sample data is fictional.** No real customer, vendor-support,
  or production device data was used anywhere in these fixtures.
