# Prompt for Team Member 2 — PRISM Research, Data, Fixtures, and Documentation

You are Team Member 2 for PRISM (Proactive Risk Intelligence System Management), an AI-assisted, vendor-agnostic network-device compliance engine.

The repository is already initialized on `main`. Do not repeat setup, cloning, GitHub creation, package initialization, or initial commits. Work in:

```text
/Users/swarnavchatterjee/Documents/CODING/PRISM
```

## Mission and ownership

Support the primary developer with verified security knowledge, vendor examples, realistic fixtures, and documentation.

The system pipeline is:

```text
configuration upload → normalization → canonical baseline schema
→ compliance rules → human review of unknown lines
→ learned mappings → findings and reports
```

The primary developer owns the core implementation. Do not build a competing engine or redesign these files:

```text
src/schema/baseline.py
src/normalization/engine.py
src/normalization/patterns.py
src/compliance/engine.py
```

Your work is primarily research, YAML data, fixtures, documentation, and supporting tests.

## 1. Final CIS MVP control set

Research and select approximately 15–20 high-value network-device controls. Do not reproduce the entire CIS benchmark. Choose controls that are meaningful, representable by the current schema, testable with simple operators, and useful in a live demo.

Cover categories such as remote access, authentication, logging, access control, management-plane security, and secure defaults.

For every control record:

- Stable control ID
- Name and category
- Benchmark/version, if known
- Canonical schema path
- Operator and expected value
- Severity
- Cisco remediation command
- Juniper remediation command where applicable
- Short rationale
- Official source URL
- Vendor limitations

Update:

```text
data/frameworks/cis_benchmarks.yaml
```

Use this compatible structure:

```yaml
- id: CIS-1.1
  name: SSH version 2 enforced
  category: remote_access
  schema_path: baseline.remote_access.ssh_version
  operator: ==
  expected_value: 2
  severity: high
  remediation_template: ip ssh version 2
  remediation:
    cisco: ip ssh version 2
    juniper: set system services ssh
  rationale: Short explanation in your own words.
  references:
    - https://official-source.example/control
```

Do not invent benchmark IDs or citations. If a control cannot map to the existing schema, put it in `docs/schema-review.md` under `Proposed Schema Extensions` instead of forcing it into an unrelated field.

## 2. Vendor pattern libraries

Create and validate these files:

```text
data/vendor_patterns/cisco_patterns.yaml
data/vendor_patterns/juniper_patterns.yaml
```

Each pattern should contain `pattern_name`, `schema_path`, `regex`, and either `value` or `value_type`. Optional fields are `description` and `source`.

Example:

```yaml
remote_access:
  - pattern_name: ssh_version
    schema_path: baseline.remote_access.ssh_version
    regex: '^\\s*ip ssh version (\\d+)\\s*$'
    value_type: int
    description: Cisco IOS SSH protocol version
```

Cover secure and insecure states where meaningful, including SSH version 2, Telnet enabled/disabled, HTTP management enabled/disabled, AAA, syslog, and minimum password length. Anchor regexes where possible, use correct YAML types, and reference real schema paths.

## 3. Safe sample configurations

Create these files:

```text
data/sample_configs/cisco_compliant.cfg
data/sample_configs/cisco_noncompliant.cfg
data/sample_configs/juniper_compliant.set
data/sample_configs/juniper_noncompliant.set
data/sample_configs/unknown_vendor.cfg
data/sample_configs/README.md
```

Each fixture should contain 8–12 relevant security lines, comments, irrelevant lines, safe fictional values, and both recognized and unrecognized lines. The unknown-vendor fixture must intentionally contain lines requiring human training.

The README must document each file’s vendor/syntax, expected mapped controls, expected unmapped lines, expected compliance result, and assumptions. Never add credentials, API keys, real hostnames, public IPs, or customer data.

## 4. Expected results and supporting tests

Create:

```text
tests/fixtures/expected_results.yaml
```

Document expected behavior using flexible assertions where appropriate:

```yaml
cisco_compliant.cfg:
  vendor: cisco
  expected_minimum_passed: 12
  expected_unmapped_lines: 0
cisco_noncompliant.cfg:
  vendor: cisco
  expected_failed_controls:
    - CIS-1.2
  expected_minimum_failed: 2
```

If adding tests, focus on pattern coverage, boolean/integer extraction, Cisco/Juniper syntax differences, fixture expectations, and unknown-line behavior. Do not rewrite core tests without a concrete reason.

## 5. Schema review

Review `src/schema/baseline.py` and create:

```text
docs/schema-review.md
```

Document controls that map cleanly, missing fields, required-for-MVP extensions, future enhancements, naming inconsistencies, and controls that should be excluded because they cannot be normalized reliably.

The schema is a shared contract. Propose changes first; do not silently expand it.

## 6. Documentation and demo material

Create:

```text
docs/cis-control-catalog.md
docs/demo-data-guide.md
```

The catalog should explain every selected control in plain language and include its source. The demo guide should explain which file demonstrates compliance, failures, unknown-line training, expected results, remediation commands, and honest MVP limitations.

Do not claim live SSH collection, full multi-framework support, or production-scale deployment unless implemented.

## Research standards

Prefer official CIS, Cisco, Juniper, NIST, or DISA sources. Summarize requirements in your own words; do not copy large copyrighted benchmark sections. Record source URLs and access dates. If a source cannot be verified, mark it `Needs verification` rather than guessing.

The current evaluator supports operators `==`, `!=`, `>`, `<`, `>=`, `<=`, `in`, and `contains`. If you need a new operator or rule structure, document it for the primary developer instead of silently changing the engine.

Use full provenance paths consistently, such as:

```text
baseline.remote_access.ssh_version
```

## Validation checklist

From the repository root, run:

```bash
pytest -q
```

Also validate every YAML file with the available YAML parser. Confirm that every rule has required fields, every regex parses, every schema path is real or documented as a proposal, compliant fixtures do not accidentally fail, non-compliant fixtures contain explainable failures, and unknown fixtures contain unmapped lines.

Do not add secrets, `.env` files, generated databases, generated PDFs, or unrelated changes.

## Required handoff report

Create:

```text
docs/team-member-2-handoff.md
```

Include these sections:

```text
Completed
Control Set
Validation
Assumptions
Open Questions
Recommended Integration Order
```

The integration order should be:

1. Review schema proposals.
2. Review vendor patterns.
3. Review CIS rules.
4. Run pattern tests.
5. Run fixture/end-to-end tests.
6. Resolve mismatches.

## Collaboration rules

- Preserve unrelated work.
- Do not use destructive Git commands.
- Keep commits focused if you commit changes.
- Do not commit secrets, `.env` files, databases, generated PDFs, or credentials.
- If core code must change, document the request and notify the primary developer.

## Definition of done

The work is complete when the CIS control set is researched and referenced, Cisco and Juniper patterns cover the selected controls, compliant/non-compliant/unknown fixtures exist, expected outcomes are documented, schema gaps are reported, demo documentation is usable, existing tests pass, and the handoff report tells the primary developer exactly what to integrate.

> Provide verified security knowledge and realistic data. Do not guess, overclaim support, or silently modify the core architecture.
