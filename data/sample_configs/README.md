# Sample Configuration Fixtures — PRISM

All fixtures in this directory are **entirely fictional**: hostnames,
community strings, and passwords are placeholders, and every IP address
uses an RFC 5737 documentation range (`192.0.2.0/24`, `198.51.100.0/24`,
`203.0.113.0/24`). No real credentials, hostnames, public IPs, or
customer data appear anywhere in this directory.

---

## `cisco_compliant.txt`
- **Vendor/syntax:** Cisco IOS / IOS-XE, classic hierarchical CLI.
- **Expected mapped controls (pass):** CIS-1.1 (SSHv2), CIS-1.2 (no
  Telnet), CIS-1.3 (HTTP mgmt disabled), CIS-1.4 (AAA enabled),
  CIS-1.5 (password encryption), CIS-1.6 (min password length 8),
  CIS-1.7 (syslog configured), CIS-1.8 (admin access logging),
  CIS-1.9 (default-deny ACL), CIS-1.10 (ACL present), plus the
  proposed-extension controls CIS-2.1 (exec-timeout), CIS-2.2 (no
  default SNMP community), CIS-2.3 (banner), CIS-2.4 (CDP disabled),
  CIS-2.5 (RSA modulus 2048).
- **Expected unmapped lines:** 0 (every security-relevant line is
  covered by `cisco_patterns.yaml`; comment lines and interface
  description text are expected to be ignored by design, not counted
  as "unmapped").
- **Expected compliance result:** PASS on all mapped MVP controls.
- **Assumptions:** `enable secret` uses a placeholder hash string, not
  a real Type 8/9 hash — do not treat it as a working credential.

## `cisco_noncompliant.txt`
- **Vendor/syntax:** Cisco IOS.
- **Expected mapped controls (fail):** CIS-1.1 (SSHv1 in use),
  CIS-1.2 (Telnet still permitted on vty), CIS-1.3 (HTTP server
  enabled), CIS-1.4 (no `aaa new-model`), CIS-1.5 (reversible `enable
  password`, no `service password-encryption`), CIS-1.7 (no syslog
  host configured), CIS-2.1 (`exec-timeout 0 0` = never), CIS-2.2
  (default `public` community with RW), CIS-2.4 (CDP left enabled).
- **Expected unmapped lines:** 0 — every line is either a known-pattern
  match (in its failing state) or a comment/interface-description line.
- **Expected compliance result:** FAIL on the controls listed above;
  PASS is not expected on any control in this fixture.
- **Assumptions:** `enable password letmein123` is a placeholder value
  chosen to make the *type* of failure (reversible password) obvious;
  it is not a real credential and must never be reused anywhere.

## `juniper_compliant.txt`
- **Vendor/syntax:** Juniper Junos, flat `set` statement export style
  (`show configuration | display set`).
- **Expected mapped controls (pass):** Junos-applicable equivalents of
  CIS-1.1, CIS-1.2, CIS-1.3, CIS-1.4, CIS-1.6, CIS-1.7, CIS-1.8,
  CIS-1.9, CIS-1.10, CIS-2.1, CIS-2.2, CIS-2.3, CIS-2.6. Note: CIS-1.5
  (password-encryption) and CIS-2.4 (CDP) and CIS-2.5 (RSA modulus)
  are marked **not applicable** for Juniper per the vendor_limitations
  notes in `cis_benchmarks.yaml` — they should not appear as pass or
  fail, but as "N/A."
- **Expected unmapped lines:** 0.
- **Expected compliance result:** PASS on all applicable mapped MVP
  controls; N/A on the three Cisco-specific controls noted above.
- **Assumptions:** SNMP `authorization read-only` syntax assumed
  current for the Junos release being modeled; verify against a real
  device if this fixture is ever used beyond the demo.

## `juniper_noncompliant.txt`
- **Vendor/syntax:** Juniper Junos, flat `set` statement export style.
- **Expected mapped controls (fail):** CIS-1.2 (Telnet service present),
  CIS-1.3 (HTTP/J-Web management present), CIS-1.4 (no
  authentication-order configured), CIS-1.7 (no syslog host), CIS-1.9
  (firewall filter has no default-discard term), CIS-2.2 (default
  `public` community with read-write), CIS-2.6 (root SSH login
  allowed).
- **Expected unmapped lines:** 0.
- **Expected compliance result:** FAIL on the controls listed above.
- **Assumptions:** none beyond the fictional-data guarantee above.

## `unknown_vendor.txt`
- **Vendor/syntax:** Fictional "NexaOS" — invented for this fixture
  only, does not correspond to any real vendor or product, chosen so
  the demo cannot be accused of just special-casing a real third
  vendor the team happened to pre-test against.
- **Expected mapped controls:** **none** — by design, zero lines in
  this file should match any existing `cisco_patterns.yaml` or
  `juniper_patterns.yaml` regex.
- **Expected unmapped lines:** 7 security-relevant lines flagged
  `needs_training` (`zone-policy default`, `admin-access
  secure-shell`, `legacy-console-access`, `audit-stream`,
  `credential-policy`, `discovery-broadcast`, `mgmt-interface`). Two
  lines (`comment:` and `uptime-report`) are intentionally
  non-security-relevant noise and should NOT be flagged for training —
  if the training UI does flag them, that's a sign the "is this line
  worth a human's time" heuristic needs tightening.
- **Expected compliance result:** No pass/fail verdict possible before
  training; this is the point of the fixture (proves NFR3 graceful
  degradation — the pipeline must not crash or silently guess).
- **Demo usage:** after uploading this fixture, live-train 2–3 of the
  seven unmapped lines (recommended: `zone-policy default`,
  `admin-access secure-shell`, `audit-stream` — these map cleanly to
  existing schema fields) and re-run normalization to show the
  learned mapping apply immediately (NFR5).
- **Assumptions:** "NexaOS" is entirely fictional; do not present it as
  a real product in demo narration — describe it as "a vendor syntax
  we made up to prove we're not just special-casing two vendors we
  tested against."
