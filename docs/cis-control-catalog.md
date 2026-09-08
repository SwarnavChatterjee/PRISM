# CIS Control Catalog — PRISM MVP

This catalog explains, in plain language, every control PRISM checks
in its MVP demo. Full machine-readable definitions live in
`data/frameworks/cis_benchmarks.yaml`; this document is the
human-readable companion, written for a judge, teammate, or new
contributor who wants to understand *why* each control matters without
reading YAML.

Controls CIS-1.1 through CIS-1.10 are wired into the live compliance
engine today. Controls CIS-2.1 through CIS-2.6 are researched and
ready, but pending a schema extension (see `docs/schema-review.md`)
before they can be evaluated automatically — they're documented here
so the roadmap story is honest and complete, not because they run yet.

---

### CIS-1.1 — SSH version 2 enforced
**In plain terms:** the device only accepts the modern, secure version
of SSH, not the old version 1 that has known cryptographic weaknesses.
**Severity:** High. **Source:** CIS Cisco IOS Benchmark, control family
2.1.1.2 (verified against the CIS Cisco IOS 17 v1.0.0 audit list).

### CIS-1.2 — Telnet disabled
**In plain terms:** nobody can log into this device over Telnet, which
sends passwords and commands in plain, readable text over the network.
**Severity:** High. **Source:** CIS Cisco IOS Benchmark control 1.2.2;
cross-referenced against DISA's Cisco IOS XE Router NDM STIG finding
V-215845, which makes the same point generically across protocols.

### CIS-1.3 — HTTP management interface disabled
**In plain terms:** the device's web-based admin panel isn't reachable
over unencrypted HTTP (if a web panel is needed at all, it should be
HTTPS-only and access-restricted).
**Severity:** Medium. **Source:** CIS Cisco IOS Benchmark control
family 1.2.11/1.2.12.

### CIS-1.4 — AAA authentication framework enabled
**In plain terms:** logins go through a centralized authentication
system rather than one shared local password, so you can tell *who*
logged in, not just *that someone* did.
**Severity:** High. **Source:** CIS Cisco IOS Benchmark control 1.1.1.

### CIS-1.5 — Password encryption enabled
**In plain terms:** passwords stored in the device's config file are
scrambled, not sitting there in plain or trivially-reversible text for
anyone who can read the config.
**Severity:** Medium. **Source:** CIS Cisco IOS Benchmark control
1.4.2. *(Cisco-specific — see vendor limitations in the YAML; Junos
handles secret storage differently by default.)*

### CIS-1.6 — Minimum password length enforced
**In plain terms:** the device won't accept very short, easily-guessed
local passwords.
**Severity:** Medium. **Source:** General CIS password-policy
baseline — marked "Needs verification" against a single stable
control ID; verify against the current CIS Cisco IOS Benchmark PDF
before final publication.

### CIS-1.7 — Centralized syslog configured
**In plain terms:** the device sends its logs to a separate server, so
evidence of what happened survives even if the device itself is reset,
rebooted, or compromised.
**Severity:** High. **Source:** Cisco IOS logging configuration
reference; cross-check against a numbered CIS control before final
publication (see "Needs verification" note in the YAML).

### CIS-1.8 — Administrative access logging enabled
**In plain terms:** beyond just knowing someone logged in, the device
records *what commands they ran* while logged in.
**Severity:** Medium. **Source:** CIS Cisco IOS Benchmark control
family 1.1.7.

### CIS-1.9 — Default-deny access control present
**In plain terms:** traffic is blocked by default unless specifically
allowed, rather than allowed by default unless specifically blocked.
This is the single most important access-control design decision on
any perimeter device.
**Severity:** High. **Source:** CIS Cisco IOS Benchmark control family
3.2 (perimeter ACL controls).

### CIS-1.10 — At least one ACL defined
**In plain terms:** a basic sanity check — does this device have *any*
access control lists at all? A device with zero is almost certainly
unsegmented.
**Severity:** Low (intentionally a coarse smoke test, not a
substitute for CIS-1.9). **Source:** General network segmentation best
practice, consistent with CIS Controls v8 network infrastructure
management guidance.

---

## Researched but pending schema extension (CIS-2.x)

### CIS-2.1 — Exec timeout enforced
Idle admin sessions log themselves out after 10 minutes or less,
rather than staying open indefinitely on an unattended terminal.
Severity: Medium. Source: CIS Cisco IOS Benchmark controls 1.2.6–1.2.9.

### CIS-2.2 — Default SNMP community strings removed
The device doesn't still use the well-known "public"/"private" SNMP
passwords, which are essentially default credentials.
Severity: High. Source: CIS Cisco IOS Benchmark controls 1.5.2–1.5.4.

### CIS-2.3 — Legal/warning banner configured
The device displays a warning that access is monitored and
unauthorized use is prohibited — often a legal/policy requirement, not
just a technical one.
Severity: Low. Source: CIS Cisco IOS Benchmark controls 1.3.1–1.3.3.

### CIS-2.4 — CDP disabled
The device doesn't broadcast its model, OS version, and hostname to
anything plugged into the same network segment.
Severity: Low. Cisco-specific. Source: CIS Cisco IOS Benchmark control
2.1.2.

### CIS-2.5 — SSH RSA host key at least 2048 bits
The cryptographic key used to set up SSH sessions is strong enough by
current standards. Severity: Medium. Cisco-specific (not reliably
config-checkable on Junos). Source: CIS Cisco IOS Benchmark control
2.1.1.1.3.

### CIS-2.6 — SSH root login disabled
On Unix-derived platforms like Junos, nobody can SSH in directly as
"root" — they log in as a named user and escalate privileges from
there, preserving accountability.
Severity: High. Juniper/Unix-derived platforms only. Source: DISA
Juniper SRX Services Gateway NDM STIG, finding V-223212.

---

## What this catalog intentionally does not claim

PRISM's MVP does not implement live SSH collection, full NIST/DISA/ISO
multi-framework support, or production-scale multi-tenant deployment.
Those are documented as Phase 1/2 roadmap items in the system design
doc, not implemented features — see `docs/demo-data-guide.md` for the
honest, current-state breakdown.
