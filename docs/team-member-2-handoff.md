# Team Member 2 Handoff Report — PRISM

## Completed

- Researched and documented a 16-control CIS MVP set in
  `data/frameworks/cis_benchmarks.yaml`: 10 controls (CIS-1.1–1.10)
  map directly to the currently-locked Security Baseline Model schema;
  6 additional high-value controls (CIS-2.1–2.6) are fully researched
  and documented but flagged `proposed_schema_extension` pending your
  review.
- Built Cisco and Juniper vendor pattern libraries
  (`data/vendor_patterns/cisco_patterns.yaml`,
  `data/vendor_patterns/juniper_patterns.yaml`) covering all 16
  controls, with anchored regexes and real/documented schema paths.
- Built five sample config fixtures plus a README:
  `cisco_compliant.txt`, `cisco_noncompliant.txt`,
  `juniper_compliant.txt`, `juniper_noncompliant.txt`,
  `unknown_vendor.txt` (fictional "NexaOS" syntax), and
  `data/sample_configs/README.md` documenting each one's expected
  behavior.
- Built `tests/fixtures/expected_results.yaml` with per-fixture
  expected pass/fail/N/A/unmapped counts, hand-derived against the
  pattern files above.
- Wrote `docs/schema-review.md` covering clean mappings, proposed
  extensions, naming inconsistencies, a compliance-engine gap
  (`not_applicable` verdict handling), future enhancements, and
  controls explicitly excluded as unreliable to normalize.
- Wrote `docs/cis-control-catalog.md` (plain-language explanation of
  every control, live and pending) and `docs/demo-data-guide.md`
  (demo script + honest MVP limitations).

## Control Set

16 controls total. 10 live (wired to existing schema fields), 6
pending a schema extension. Full detail in
`data/frameworks/cis_benchmarks.yaml` and
`docs/cis-control-catalog.md`. Primary sources: CIS Cisco IOS
Benchmark (versions 15/16/17, verified via Tenable's published audit
mirrors and archived CIS PDFs), and the DISA Juniper SRX Services
Gateway NDM STIG (verified via stigviewer.com) used as the Juniper
cross-reference since no general-purpose CIS Junos device benchmark
with equivalent numbering was located during this research pass.

## Validation

**No live repository was available at the time this work was done**
(confirmed by the requester — working from context/specification only,
not an actual `git clone`). Because of this:

- I could **not** run `pytest -q` against real code, since
  `src/schema/baseline.py` and `src/compliance/engine.py` do not exist
  yet in a checked-out repo.
- I **did** validate every YAML file in this handoff for syntactic
  correctness (parses cleanly under a standard YAML loader) and for
  internal consistency (every `schema_path` referenced either exists
  in the Day-1 schema sketch or is explicitly flagged
  `proposed_schema_extension`; every regex is anchored and was
  mentally traced against its corresponding sample config line).
- **Action item for you:** once the repo exists, run the validation
  checklist for real — `pytest -q`, YAML-parse every file under
  `data/`, and confirm the counts in `expected_results.yaml` match
  actual pipeline output. I've labeled every hand-derived number in
  that file so you know which ones need a real re-check.

## Assumptions

- Used the Day-1 schema sketch from the implementation plan as the
  ground truth for `schema_path` values, since the actual
  `src/schema/baseline.py` wasn't available to inspect directly.
- Assumed Junos config fixtures should use the flat `set` export style
  (`show configuration | display set`), since that's the most common
  format teams script against.
- For controls where I could not confirm one stable CIS control ID
  across benchmark versions (min password length, syslog
  configuration, ACL-presence-as-a-smoke-test), I marked the citation
  "Needs verification" rather than inventing a number. Please
  double-check these against whichever exact CIS Cisco IOS Benchmark
  version your team standardizes on.
- Treated CIS-1.5, CIS-2.4, and CIS-2.5 as Cisco-only, and CIS-2.6 as
  Juniper/Unix-derived-only, with `not_applicable` as the expected
  verdict rather than pass or fail — this requires a small
  compliance-engine change (see schema-review.md) that I'm flagging,
  not implementing.

## Open Questions

1. Does the compliance engine currently support a `not_applicable`
   verdict, or only pass/fail/unmapped? If not, this needs a decision
   before the Juniper fixtures can produce a fully correct demo
   output (see `docs/schema-review.md`, "Vendor-not-applicable
   handling").
2. Do you want the 6 proposed-extension controls (CIS-2.1–2.6) wired
   into the schema before demo day, or held as a documented roadmap
   item only? Either is defensible; it changes how much normalizer
   work is left.
3. Is there a preferred exact CIS Cisco IOS Benchmark version
   (15/16/17) the team wants to standardize citations against? I
   verified controls across multiple versions since the numbering
   shifts slightly release to release.
4. Can you confirm the actual field names in the real
   `src/schema/baseline.py` match the Day-1 sketch once it's
   committed? If any field was renamed during implementation, the
   `schema_path` values throughout `cis_benchmarks.yaml` and both
   vendor pattern files will need a global find-and-replace.

## Recommended Integration Order

1. Review schema proposals (`docs/schema-review.md`) — decide on the
   6 CIS-2.x extensions and the `not_applicable` verdict handling
   before anything else, since later steps depend on these decisions.
2. Review vendor patterns (`data/vendor_patterns/cisco_patterns.yaml`,
   `juniper_patterns.yaml`) against the real, committed
   `src/normalization/patterns.py` matching logic.
3. Review CIS rules (`data/frameworks/cis_benchmarks.yaml`) against
   the real, committed `src/compliance/engine.py` operator support.
4. Run pattern tests against the sample configs in
   `data/sample_configs/`.
5. Run fixture/end-to-end tests using
   `tests/fixtures/expected_results.yaml` as the assertion source —
   re-derive any numbers flagged as hand-counted before trusting them.
6. Resolve mismatches, prioritizing the four Open Questions above.
