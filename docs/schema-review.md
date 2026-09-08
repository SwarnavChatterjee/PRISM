# Schema Review — PRISM Security Baseline Model

**Reviewer:** Team Member 2
**Reviewed against:** the Security Baseline Model as specified in the
Day-1 implementation plan (`src/schema/baseline.py` target structure).
No live repository was available at review time — this review is
based on the JSON schema sketch below, which was the locked contract
from the Day-1 design session. **Re-run this review against the actual
committed `baseline.py` as soon as it exists**, since field names or
nesting may have shifted slightly during implementation.

```json
{
  "device": {"hostname": "", "vendor": "", "os_version": "", "serial_number": ""},
  "baseline": {
    "remote_access": {"ssh_version": null, "telnet_enabled": null, "http_management_enabled": null},
    "authentication": {"password_encryption": null, "min_password_length": null, "aaa_enabled": null},
    "logging": {"admin_access_logging": null, "syslog_configured": null},
    "access_control": {"acl_count": null, "default_deny_present": null}
  },
  "unmapped_lines": [{"line_no": 0, "raw": "", "status": "needs_training"}],
  "provenance": {"ssh_version": {"source_line": 0, "raw": ""}},
  "metadata": {"scan_timestamp": "", "scanned_by": "", "device_id": ""}
}
```

---

## Controls that map cleanly

These CIS MVP controls (see `data/frameworks/cis_benchmarks.yaml`,
Group 1) resolve directly to a `schema_path` that already exists in
the locked schema:

| Control | schema_path |
|---|---|
| CIS-1.1 | `baseline.remote_access.ssh_version` |
| CIS-1.2 | `baseline.remote_access.telnet_enabled` |
| CIS-1.3 | `baseline.remote_access.http_management_enabled` |
| CIS-1.4 | `baseline.authentication.aaa_enabled` |
| CIS-1.5 | `baseline.authentication.password_encryption` |
| CIS-1.6 | `baseline.authentication.min_password_length` |
| CIS-1.7 | `baseline.logging.syslog_configured` |
| CIS-1.8 | `baseline.logging.admin_access_logging` |
| CIS-1.9 | `baseline.access_control.default_deny_present` |
| CIS-1.10 | `baseline.access_control.acl_count` |

This is a healthy ratio — 10 of the 16 researched controls need zero
schema change, which suggests the Day-1 schema lock-in was well
scoped for the CIS taxonomy.

---

## Missing fields / required-for-MVP extensions

Six controls (CIS-2.1 through CIS-2.6 in `cis_benchmarks.yaml`) are
genuinely high-value and commonly cited across CIS/DISA sources, but
have no home in the current schema. **Proposed additions**, grouped by
where they'd naturally live:

```json
"baseline": {
  "remote_access": {
    "exec_timeout_minutes": null,        // CIS-2.1
    "rsa_key_modulus_bits": null,        // CIS-2.5 (Cisco-only, config-checkable)
    "root_ssh_login_enabled": null       // CIS-2.6 (Juniper/Unix-derived platforms)
  },
  "management": {                        // NEW top-level baseline section
    "snmp_default_community_present": null,  // CIS-2.2
    "banner_configured": null,               // CIS-2.3
    "cdp_enabled": null                      // CIS-2.4 (Cisco-only)
  }
}
```

I recommend a new `baseline.management` section rather than
overloading `remote_access`, since banner/CDP/SNMP-community are
management-plane hygiene controls, not remote-access-protocol
controls — keeping the taxonomy clean will matter once a second
framework (NIST) gets mapped onto the same schema in Phase 1.

**This is a proposal, not a change.** Please confirm with the primary
developer before touching `baseline.py`. Until confirmed, the six
CIS-2.x controls in `cis_benchmarks.yaml` are flagged
`status: proposed_schema_extension` and must NOT be wired into
`src/compliance/engine.py`.

---

## Naming inconsistencies to watch for

- The Day-1 schema sketch mixes verb-tense styles across booleans:
  `telnet_enabled` (state-of-being) vs. `password_encryption` (noun,
  implicitly "is enabled"). Recommend standardizing all new boolean
  fields on the `<noun>_enabled` / `<noun>_present` pattern going
  forward (matches what I used for the proposed extensions above) so
  the compliance engine's default "expected_value: true/false" logic
  reads consistently.
- `acl_count` is an integer while everything else in `access_control`
  is a boolean — worth a one-line comment in `baseline.py` clarifying
  that this is intentionally a coarse smoke-test signal (see CIS-1.10
  rationale) and not meant to carry the same weight as
  `default_deny_present`.

---

## Vendor-not-applicable handling — a schema/engine gap, not just data

Several controls (CIS-1.5, CIS-2.4, CIS-2.5 for Juniper; CIS-2.6 for
Cisco) are legitimately **not applicable** for one vendor, not merely
"failed" or "unmapped." The current schema/engine design (as
described in the implementation plan) only distinguishes pass/fail/
unmapped. I recommend the compliance engine support a third verdict,
`not_applicable`, keyed off a `vendor_limitations` field already
present in `cis_benchmarks.yaml`. Without this, cross-vendor demo
runs will either wrongly show Juniper "failing" a Cisco-only control,
or the CIS YAML has to silently omit real per-vendor context to avoid
that — the latter is worse, since it throws away genuinely useful
documentation. **Flagging this to the primary developer as a
compliance-engine change request, not implementing it myself.**

---

## Future enhancements (explicitly out of MVP scope)

- LLDP-based discovery-protocol equivalent to CIS-2.4 for non-Cisco
  platforms (mentioned in `cisco_patterns.yaml` CDP notes).
- A `password_complexity` field (seen as a gap in the `unknown_vendor.cfg`
  fixture's `credential-policy complexity=high` line, which has
  nowhere to map today).
- Confidence scoring per field (`Section 5.5` of the system design doc)
  — the current schema has no place to store "how sure are we" per
  value; only `provenance.<field>.raw` for a source-line pointer.
  Recommend a future `confidence: float` sibling key inside each
  provenance entry.

---

## Controls excluded because they cannot be normalized reliably

- CIS-2.5 (RSA key modulus) for **Juniper**: Junos SSH host keys are
  not typically expressed as a plain, operator-set config line the
  way Cisco's `crypto key generate rsa modulus 2048` is — there's no
  reliable static-config signal to regex against. Recommend excluding
  this control entirely for Juniper rather than guessing, and marking
  it `not_applicable` in the fixture/expected-results data (already
  done in `tests/fixtures/expected_results.yaml`).
- Any control requiring live device state (e.g. "current session
  count," "uptime since last config change") is out of scope for a
  static-config-dump pipeline by definition — noted here so it isn't
  proposed again in Phase 1 planning by mistake.
