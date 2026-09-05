# AI-Augmented Vendor-Agnostic Network Compliance Engine
## Complete System Design — From Base to Advanced

---

## 0. How to Use This Document
This is written in layers: **Base** (what you must get right to have a working MVP), **Intermediate** (what makes it good), **Advanced** (what makes it defensible as a "real product" in front of judges/investors). Read top to bottom once, then use it as a reference during build. Sections marked ⚠️ are common failure points in projects like this.

---

## 1. Problem Restated (Precisely)

Input: a raw, unstructured configuration file/dump from *any* network device (unknown vendor, unknown syntax, unknown OS version).
Output: a structured compliance verdict (pass/fail/severity + remediation) against a chosen security framework (CIS/NIST/STIG/ISO) — **without a human writing a parser for that specific vendor first.**

The hard part is not "check config against rules." That's a lookup table. The hard part is:
**"Understand text you've never seen the shape of before, well enough to reason about it — and get smarter every time you fail."**

That reframe matters: this is fundamentally an **information extraction + semantic normalization** problem, with compliance-checking as a downstream consumer. Design the system around that truth, not around "PDF report generator with AI branding."

---

## 2. Requirements

### Functional
- FR1: Ingest single or bulk config files (text-based CLI dumps at minimum; stretch — live device pull via SSH).
- FR2: Normalize arbitrary vendor syntax into a canonical, vendor-neutral schema.
- FR3: Evaluate the canonical schema against a selectable compliance framework.
- FR4: Detect and surface unrecognized/unparseable lines rather than silently dropping them.
- FR5: Provide a human-in-the-loop interface to label unrecognized lines, and persist that mapping for future re-use.
- FR6: Generate a per-device PDF report: identity, findings, severity, remediation commands.
- FR7: Support addition of new vendors/frameworks without code redeployment.

### Non-Functional
- NFR1: **Extensibility** — adding a vendor = data/config change, not code change (this is the whole point of the project; violate it and you've built a normal parser).
- NFR2: **Explainability** — every pass/fail verdict must trace back to the exact source config line(s). Judges will ask "how do you know this is right?" — you need a receipt, not a black box.
- NFR3: **Graceful degradation** — unknown input never crashes the pipeline; it degrades to "needs training," never to an error page.
- NFR4: **Auditability** — store raw input, normalized output, and verdict together (compliance tooling lives and dies on audit trails).
- NFR5: **Low-latency feedback** in the training loop — the human labeling a line should see the system apply that learning immediately (this is your demo's "wow" moment; don't make it require a batch retrain).

---

## 3. High-Level Architecture

```
                         ┌─────────────────────────┐
                         │   1. INGESTION LAYER     │
                         │  (file upload / SSH pull)│
                         └────────────┬─────────────┘
                                      │ raw config text
                                      ▼
                         ┌─────────────────────────┐
                         │ 2. NORMALIZATION ENGINE  │◄──────────┐
                         │  (rules + NLP/LLM hybrid)│           │
                         └────────────┬─────────────┘           │
                       matched lines  │  unmatched lines         │
                                      │        │                 │
                                      ▼        ▼                 │
                     ┌────────────────────┐ ┌───────────────────┴─┐
                     │ Canonical Schema    │ │ 5. TRAINING LOOP     │
                     │ (Security Baseline  │ │ (Human-in-the-loop   │
                     │  Model, JSON)       │ │  labeling GUI)       │
                     └──────────┬──────────┘ └──────────────────────┘
                                │                     │ new mapping rule
                                ▼                     │ (persisted back into
                     ┌─────────────────────────┐      │  Normalization Engine's
                     │ 3. COMPLIANCE ENGINE     │      │  knowledge store)
                     │ (rules diff vs framework)│◄─────┘
                     └──────────┬───────────────┘
                                │ findings (pass/fail/severity)
                                ▼
                     ┌─────────────────────────┐
                     │ 4. REPORTING ENGINE      │
                     │  (PDF: findings + fixes) │
                     └─────────────────────────┘

                     ┌─────────────────────────┐
                     │ 6. DASHBOARD / FRONTEND  │  (wraps 1, 4, 5 for the user)
                     └─────────────────────────┘

                     ┌─────────────────────────┐
                     │ 0. KNOWLEDGE STORE       │  (persists: vendor syntax
                     │  (DB, versioned)         │   mappings, framework rules,
                     └─────────────────────────┘   learned patterns, audit log)
```

The **Knowledge Store** is the real product. Ingestion, normalization, compliance, and reporting are stateless-ish pipelines that read/write it. Everything else is UI around it.

---

## 4. Component-by-Component Design

### 4.1 Ingestion Layer
- **Base:** accept `.txt`/`.cfg`/pasted text uploads. Detect vendor family heuristically (banner strings, prompt style, keyword frequency: `set` = Juniper-style, `interface GigabitEthernet` = Cisco-style, etc.) — this pre-classification massively narrows the normalization search space; don't skip it.
- **Intermediate:** bulk upload (zip of configs), tag each with metadata (hostname, IP, uploaded-by, timestamp).
- **Advanced:** live pull via **Netmiko** (SSH, broad multi-vendor driver support) or **NAPALM** (higher-level, normalized getters, but supports fewer vendors than Netmiko). ⚠️ Tradeoff: NAPALM gives you *some* normalization for free on supported vendors, which conflicts with your pitch of "we normalize everything ourselves." Use Netmiko for raw collection to keep your AI normalization the actual hero of the demo.

### 4.2 Normalization Engine (the core IP)
This is where most design tradeoffs live — see Section 5 for the deep dive. Structurally:
- **Input:** raw config text + vendor-family hint from ingestion.
- **Process:** line-by-line (or block-by-block) classification into one of: *known pattern (regex/rule match)* → *fuzzy/semantic match (embedding similarity to known patterns)* → *unrecognized (route to training loop)*.
- **Output:** canonical JSON per device conforming to the Security Baseline Schema (4.3), plus a list of `unmapped_lines` with their raw text and line numbers.

### 4.3 Security Baseline Schema (canonical model)
Design this **before** writing any parser — it's your contract between normalization and compliance. Example shape:

```json
{
  "device": {
    "hostname": "core-sw-01",
    "vendor": "cisco",
    "os_version": "IOS-XE 17.6",
    "serial_number": "FXS12345"
  },
  "baseline": {
    "remote_access": {
      "ssh_version": 2,
      "telnet_enabled": false,
      "http_management_enabled": false
    },
    "authentication": {
      "password_encryption": "type8",
      "min_password_length": 8,
      "aaa_enabled": true
    },
    "logging": {
      "admin_access_logging": true,
      "syslog_configured": true
    },
    "access_control": {
      "acl_count": 4,
      "default_deny_present": true
    }
  },
  "unmapped_lines": [
    {"line_no": 42, "raw": "set security zone dmz screen block-tcp", "status": "needs_training"}
  ],
  "provenance": {
    "ssh_version": {"source_line": 12, "raw": "ip ssh version 2"}
  }
}
```
⚠️ **The `provenance` block is not optional** — it's what makes your compliance findings explainable/auditable (NFR2, NFR4), and it's what your remediation engine uses to generate device-specific fix commands.

**Tradeoff — schema breadth vs depth:** Don't try to model every possible security setting across every vendor upfront. Pick ~15–20 high-signal controls that appear across CIS/NIST/STIG for network devices (SSH version, Telnet disabled, password complexity, AAA, logging, ACL/default-deny, NTP, banner/warning message, SNMP community strings, unused port shutdown). Depth on these beats breadth across hundreds of obscure ones — both for engineering time and for demo clarity.

### 4.4 Compliance Engine
- **Design as a rules table, not code.** Store framework requirements as data:
```yaml
- id: CIS-1.1
  control: "SSH version 2 enforced"
  schema_path: baseline.remote_access.ssh_version
  operator: "=="
  expected: 2
  severity: high
  remediation_template: "ip ssh version 2"
```
- The engine just walks this table against the normalized JSON. Adding a new framework = adding a new YAML file, not new code. This directly satisfies FR7/NFR1 and is an easy thing to point to when judges ask "how do you support NIST *and* CIS?"
- **Remediation generation:** `remediation_template` should be parameterized per vendor (a small vendor→syntax lookup) so the same logical rule produces `ip ssh version 2` for Cisco vs `set system services ssh root-login deny` style syntax for Juniper.

### 4.5 Training Loop (your differentiator — design this carefully)
This is what separates you from "just another compliance scanner." Design requirements:
1. When normalization can't confidently match a line, it should **not guess silently** — it goes to `unmapped_lines`.
2. Admin sees the raw line + surrounding context (2–3 lines before/after help a human infer intent) + a dropdown of known schema categories (`remote_access.ssh_version`, `logging.admin_access_logging`, etc.) + "create new category" escape hatch.
3. On submit, store the mapping as `(vendor_family, pattern/regex-generalized-from-line) → schema_path` in the Knowledge Store.
4. **Immediately re-run normalization** on the current file so the demo shows the line flip from "unmapped" to "mapped" live — this is the moment that sells the whole pitch.
5. Persist this mapping so the *next* config from that vendor family benefits automatically — this is what makes it "learning" rather than "one-off manual override."

⚠️ Common failure: teams build this as "admin edits a JSON file" — that's not a GUI, that's config editing with extra steps. It needs to feel like Duolingo-style guided labeling, not YAML surgery.

### 4.6 Reporting Engine
- Use **ReportLab** (fine-grained layout control) over FPDF for anything beyond a plain table — you'll want a title page, findings table with color-coded severity, and a remediation appendix.
- Structure: Device ID page → Executive summary (pass %, critical count) → Detailed findings table (control, status, severity, source line) → Remediation appendix (copy-pasteable CLI blocks, grouped by device).
- Generate from a template + the compliance engine's output — never hand-write text into the PDF generator; keep it data-driven like everything else.

### 4.7 Dashboard/Frontend
- Base: Streamlit is genuinely fine for a 5-day hackathon (fast, Python-native, no separate frontend team needed) — don't over-invest in React unless someone already has it half-built.
- Screens needed: Upload → Processing/Status → Training Interface (for unmapped lines) → Results/Report download. Four screens, not more.

---

## 5. Key Architectural Tradeoffs (the part judges will actually probe)

### 5.1 Regex/rules vs. classic NLP vs. LLM-based normalization
| Approach | Pros | Cons | When to use |
|---|---|---|---|
| **Regex/keyword rules** | Fast, deterministic, zero cost, fully explainable | Doesn't generalize; brittle to phrasing changes | First-pass matcher for known vendors (Cisco/Juniper) — handles majority case cheaply |
| **Classic NLP (spaCy NER, embedding similarity)** | Generalizes better than regex; can match "similar" unseen lines to known categories via vector similarity | Needs some training data per category; harder to explain than regex | Second-pass fuzzy matcher: "this unmapped line is 85% similar to a known SSH-related line" |
| **LLM-based (few-shot prompting)** | Best generalization to genuinely novel vendors with zero prior examples; can explain its own reasoning in the training UI | Cost, latency, non-determinism, needs prompt-injection guardrails since you're feeding it arbitrary text | Fallback tier when regex + embedding both fail, or to *pre-fill a suggestion* for the human trainer to confirm rather than auto-accept |

**Recommended hybrid (this is your strongest architectural talking point):** three-tier cascade — regex first (cheap, fast, covers known vendors) → embedding similarity second (catches near-variants) → LLM-assisted suggestion third (only for genuinely unseen structure, and *always* surfaced to the human for confirmation, never auto-committed). This directly answers the "why not just use ChatGPT for everything" question judges will ask: cost, latency, and explainability all argue for regex-first, LLM-last.

### 5.2 Static file analysis vs. live device connection
- Static (upload a config dump): simpler, safer (no live credentials needed), works for the demo, matches "audit" use case.
- Live (SSH pull via Netmiko): more impressive, more realistic to production compliance tools, but adds credential management, network access, and vendor-driver-support risk into a 5-day timeline.
- **Recommendation:** static for the MVP/demo; mention live-pull as the "Phase 2" roadmap item in your architecture doc. Don't build both under time pressure — reliability of the live-pull path is a demo-day risk you don't need.

### 5.3 Monolith vs. microservices
- With 5 people and 5 days: **modular monolith**. Four Python modules (ingest, normalize, comply, report) behind clean function interfaces, one process, one deploy. Microservices buy you nothing here except deployment complexity and integration bugs to debug under time pressure.
- Keep the modules genuinely decoupled by contract (the JSON schema is the contract) so it *could* become microservices later — that's the "scalable architecture" story for your PPT without paying the cost now.

### 5.4 Where to persist the Knowledge Store
- SQLite for the hackathon (zero setup, file-based, trivially portable for a demo laptop). Postgres if someone already knows it well and multi-user concurrent access matters to your story.
- Schema: `vendor_patterns(vendor, raw_pattern, schema_path, confidence, created_by, created_at)`, `framework_rules(framework, control_id, schema_path, operator, expected, severity)`, `devices`, `scan_results`, `audit_log`.
- ⚠️ Version your `vendor_patterns` table changes (even just an incrementing `version` column) — "the system learns and remembers its learning history" is a strong, cheap-to-implement talking point.

### 5.5 Confidence scoring and false positives
- Every normalized field should carry a confidence score, not just a value. A regex-exact-match is confidence 1.0; an embedding-similarity match might be 0.7; an LLM suggestion pending human confirmation is "unconfirmed."
- The Compliance Engine should be configurable to only "hard fail" on high-confidence matches and flag low-confidence matches as "needs review" rather than a false pass/fail — this avoids the credibility-killing scenario of confidently stating a wrong verdict.

### 5.6 Human-in-the-loop trust boundary
- Never let the system silently auto-learn from an LLM guess without a human confirming — this is both a correctness issue (LLM hallucination) and a security issue (a malicious/malformed config shouldn't be able to poison your Knowledge Store for future scans of *other* customers' devices). Design the training loop as **suggest → confirm → persist**, never **suggest → auto-persist**.

---

## 6. Suggested Tech Stack (with rationale)

| Layer | Choice | Why |
|---|---|---|
| Core language | Python | Netmiko/NAPALM, spaCy, ReportLab, Streamlit all live here — one language, one team velocity |
| Data collection | Netmiko | Broadest multi-vendor SSH driver support |
| Normalization (rules tier) | Python `re` + a small DSL/YAML of patterns per vendor | Explainable, fast, easy to extend by adding YAML, not code |
| Normalization (fuzzy tier) | `sentence-transformers` (embeddings) + cosine similarity | Lightweight, runs locally, no API cost, good enough for "is this similar to a known line" |
| Normalization (LLM tier, optional/stretch) | Anthropic API (Claude) via a single few-shot prompt | Used sparingly (fallback only) to control cost/latency |
| Rules storage | YAML files (or SQLite table) per framework | Non-engineers can read/extend rules; version-controllable |
| Compliance engine | Plain Python rule evaluator over the YAML | No need for a heavyweight rules engine (e.g. Drools) at this scale |
| Reporting | ReportLab | Fine-grained PDF layout control |
| Frontend | Streamlit | Fastest path to a working multi-screen UI in Python, good enough for demo polish |
| Storage | SQLite | Zero-ops, portable, sufficient for hackathon scale |

---

## 7. Compliance Framework Notes (what to actually read)

You don't need to master full CIS/NIST/STIG documents — extract the ~15–20 controls that are (a) common across all four frameworks and (b) syntactically checkable from a config file alone (not physical security or process controls, which no config parser can verify). Focus areas to read up on:
- **CIS Benchmarks for network devices** (Cisco IOS/IOS-XE benchmark is the most accessible starting point — free PDF from CIS).
- **NIST SP 800-53**, control families `AC` (Access Control), `IA` (Identification & Authentication), `AU` (Audit & Accountability), `SC` (System & Communications Protection) — these map cleanly to config-checkable items.
- **DISA STIGs** for network devices (Cisco/Juniper STIGs are public) — very config-line-specific, good source of concrete remediation command text.
- **ISO/IEC 27001 Annex A** — much higher-level/organizational; only a few controls (e.g. A.13 network security management) are config-checkable — don't over-promise ISO coverage.

Practical approach: build one internal **rule taxonomy** (your ~15–20 canonical controls) and then map each framework's specific control IDs onto that taxonomy — this is exactly what your `framework_rules` YAML tables do, and it's a genuinely good, honest answer to "how do you support 4 frameworks" (you support one taxonomy, mapped four ways).

---

## 8. Phased Roadmap (Base → Advanced)

**Phase 0 (MVP — what you must demo):**
Static config upload → regex-based normalization for 2 known vendors → CIS-only compliance check → training loop for a 3rd unknown vendor demoed live → PDF report.

**Phase 1 (Intermediate — strengthens the pitch):**
Add embedding-similarity fuzzy matching tier, add a 2nd framework (NIST) via the taxonomy mapping, add confidence scoring to findings, add bulk upload.

**Phase 2 (Advanced — the roadmap slide):**
Live device pull via Netmiko, LLM-assisted suggestion tier in the training loop, multi-tenant Knowledge Store with per-org isolation, trend dashboards (compliance drift over time), CI/CD-style integration (auto-scan on config change via webhook).

Put Phase 1/2 explicitly on a "Future Roadmap" slide — judges reward teams that clearly know what they *didn't* build and why, over teams that vaguely claim everything works.

---

## 9. Explainability & Demo Script Tie-In
Structure your live demo to *prove* the architecture, not just show a UI:
1. Upload a Cisco config → show pass/fail with source-line citations (proves normalization + provenance).
2. Upload a config from a vendor the system has never seen → show it correctly flags unmapped lines instead of guessing (proves NFR3, graceful degradation).
3. Train it live on 2–3 of those lines → re-run → show it now passes/fails correctly (proves the core differentiator).
4. Show the generated PDF with remediation commands (proves end-to-end value).

This script directly maps to Sections 4.5 and 5.6 above — the whole system design exists to make this 90-second demo credible.

---

## 10. Notes / Reading List for the Team
- **Netmiko docs** — device connection handler list, supported vendors (ktbyers.github.io/netmiko).
- **NAPALM docs** — for understanding what "already normalized" looks like, useful for schema design ideas even if not used directly.
- **CIS Benchmarks (Cisco IOS/IOS-XE)** — free PDF, best source of concrete, checkable rules.
- **sentence-transformers docs** — for the embedding-similarity fuzzy-matching tier.
- **ReportLab user guide** — PDF generation patterns (tables, styles, multi-page).
- **spaCy NER quickstart** — if going classic-NLP route instead of/alongside embeddings for the fuzzy tier.
- General reading: any article on "config drift detection" or "network configuration compliance tools" (e.g. how tools like RunZero, Forward Networks, or open-source Batfish approach multi-vendor config parsing) — useful for framing your novelty (they're mostly rule-based/vendor-specific; your active-learning loop is the gap you're filling).
