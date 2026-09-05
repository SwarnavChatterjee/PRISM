# Final Implementation Plan
### Complete Day-by-Day Execution Guide (5 Days, 5 People)

*This is your actual execution blueprint. Print this, pin it on the wall, reference it constantly. Every line below is actionable.*

---

## 0. Pre-Day 1 Setup (Do this before Day 1 starts)

**All team members do this:**
1. Clone the starter repo structure below to your machine.
2. Install Python 3.11+, pip, virtualenv.
3. Everyone reviews the lecture notes (Part 1) and tech stack doc (Section 2 & 14) once.
4. Do NOT start coding yet. Day 1 is design-only.

**Repository structure (create this today):**
```
compliance-engine/
├── README.md
├── requirements.txt
├── setup.py
├── .env.example
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── uploader.py          # File upload handling
│   ├── normalization/
│   │   ├── __init__.py
│   │   ├── engine.py            # Main normalizer
│   │   ├── patterns.py          # Pattern matching (regex tier)
│   │   ├── embeddings.py        # Embedding similarity (fuzzy tier)
│   │   └── llm_fallback.py      # Claude API tier
│   ├── schema/
│   │   ├── __init__.py
│   │   ├── baseline.py          # Security Baseline Model (JSON schema)
│   │   └── validators.py        # Pydantic/marshmallow validation
│   ├── compliance/
│   │   ├── __init__.py
│   │   ├── engine.py            # Rule evaluation
│   │   ├── framework_loader.py  # Load YAML framework rules
│   │   └── remediation.py       # Generate fix commands
│   ├── training/
│   │   ├── __init__.py
│   │   └── loop.py              # Human-in-the-loop labeling
│   ├── reporting/
│   │   ├── __init__.py
│   │   ├── pdf_generator.py     # ReportLab PDF generation
│   │   └── templates/
│   │       └── report_template.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── models.py            # SQLAlchemy/Pydantic DB models
│   │   └── db.py                # Database connection
│   └── utils/
│       ├── __init__.py
│       ├── logging.py
│       └── config.py
│
├── data/
│   ├── frameworks/
│   │   ├── cis_benchmarks.yaml  # Rule definitions
│   │   ├── nist_sp800_53.yaml
│   │   └── sample_mappings.yaml
│   ├── vendor_patterns/
│   │   ├── cisco_patterns.yaml
│   │   ├── juniper_patterns.yaml
│   │   └── generic_patterns.yaml
│   ├── sample_configs/          # Test configs for demo
│   │   ├── cisco_switch.cfg
│   │   ├── juniper_firewall.cfg
│   │   └── unknown_device.cfg
│   └── embeddings/
│       └── embeddings_cache.pkl # Cached embedding vectors
│
├── frontend/
│   ├── streamlit_app.py         # Main UI entry point
│   ├── pages/
│   │   ├── 01_upload.py
│   │   ├── 02_training.py
│   │   └── 03_results.py
│   └── assets/
│       └── logo.png
│
├── tests/
│   ├── __init__.py
│   ├── test_normalization.py
│   ├── test_compliance.py
│   └── test_integration.py
│
├── docs/
│   ├── ARCHITECTURE.md           # Architecture document (2 pages)
│   ├── SETUP.md                  # Readme with setup instructions
│   └── DEMO_SCRIPT.md            # Live demo script
│
└── database/
    └── schema.sql               # SQLite schema init
```

**Pre-Day 1 assignment:**
- **Architect:** Confirm the directory structure above makes sense, reserve 2 hours Monday morning for design sync.
- **Backend Dev:** Prepare empty stub files for your modules (ingestion, compliance, reporting).
- **AI/NLP Dev:** Prepare stub files for normalization modules.
- **Frontend Dev:** Prepare stub Streamlit app with empty page templates.
- **Research Lead:** Gather 2–3 sample configs (Cisco, Juniper, one "unknown" vendor like Arista or a SONiC switch) that will become your demo files.

---

## DAY 1: Design & Schema Lock-In

**Duration:** ~4 hours (morning/early afternoon)

**Outcome:** by end of Day 1, everyone can draw the pipeline on a whiteboard and code cannot begin until this is done wrong-free.

### 1.1 — Architect + Full Team (1 hour)
**Meeting: Project Walkthrough**

Walk through the lecture notes Part 2 (Steps 1–6) as a team, live, on a call.
- **Architect draws this on screen (real diagram or ASCII art):**
```
Upload → Ingest+Guess Vendor → Normalize → Standard Format → Check Rules → Train if Unknown → Report PDF
```

**Architect explains each arrow:**
- What goes in? What comes out? Who owns this?
- Everyone needs to understand the data flow, not just their part.

**Action items:**
- Everyone affirms they understand the six steps.
- Architect creates a shared Figma/Excalidraw diagram (doesn't need to be beautiful, needs to be shared).

### 1.2 — Research Lead (1 hour)
**Task: Lock in Security Baseline Schema**

Research Lead + Architect sit together and finalize the canonical JSON schema (the "standard format" from Step 3). This is non-negotiable — everything else depends on it.

**Schema must include:**
```json
{
  "device": {
    "hostname": "",
    "vendor": "",
    "os_version": "",
    "serial_number": ""
  },
  "baseline": {
    "remote_access": {
      "ssh_version": null,
      "telnet_enabled": null,
      "http_management_enabled": null
    },
    "authentication": {
      "password_encryption": null,
      "min_password_length": null,
      "aaa_enabled": null
    },
    "logging": {
      "admin_access_logging": null,
      "syslog_configured": null
    },
    "access_control": {
      "acl_count": null,
      "default_deny_present": null
    }
  },
  "unmapped_lines": [
    {"line_no": 0, "raw": "", "status": "needs_training"}
  ],
  "provenance": {
    "ssh_version": {"source_line": 0, "raw": ""}
  },
  "metadata": {
    "scan_timestamp": "",
    "scanned_by": "",
    "device_id": ""
  }
}
```

**Deliverable:** Write this schema to `src/schema/baseline.py` as a Pydantic model (or plain dict, but Pydantic is better for validation).

```python
# src/schema/baseline.py (pseudocode)
from pydantic import BaseModel
from typing import Optional, List

class RemoteAccess(BaseModel):
    ssh_version: Optional[int] = None
    telnet_enabled: Optional[bool] = None
    http_management_enabled: Optional[bool] = None

class Baseline(BaseModel):
    remote_access: RemoteAccess
    # ... other sections ...

class DeviceConfig(BaseModel):
    device: dict
    baseline: Baseline
    unmapped_lines: List[dict]
    provenance: dict
    metadata: dict

# When someone uses this model:
# config = DeviceConfig(**json_data)  # Validates automatically
```

**Why Pydantic:** Automatic validation (invalid data gets rejected), automatic JSON serialization, and it's the lingua franca of Python APIs.

### 1.3 — AI/NLP Dev (45 minutes)
**Task: Sketch the three-tier normalization pipeline**

Write the function signatures (not the implementation) that the normalization engine will call. This is the contract everyone else will depend on.

```python
# src/normalization/engine.py (pseudocode/stubs)

def normalize_config(raw_text: str, vendor_hint: str = None) -> DeviceConfig:
    """
    Main entry point. Takes raw config text and returns a normalized DeviceConfig.
    Internally tries three tiers: regex → embedding → LLM.
    """
    pass

def tier1_exact_match(line: str, vendor: str) -> Optional[Tuple[str, float]]:
    """
    Regex/pattern matching tier.
    Returns: (schema_path, confidence) or None if no match.
    Example output: ("remote_access.ssh_version", 1.0)
    """
    pass

def tier2_fuzzy_match(line: str, known_patterns: List[str]) -> Optional[Tuple[str, float]]:
    """
    Embedding similarity tier.
    Returns: (schema_path, confidence) or None if confidence below threshold.
    """
    pass

def tier3_llm_suggestion(line: str, known_categories: List[str]) -> Optional[Tuple[str, float]]:
    """
    Claude API tier — ONLY called if tier1 and tier2 fail.
    Returns suggestion + confidence score, but is NEVER auto-committed (always human review).
    """
    pass
```

**Deliverable:** Save these function stubs to `src/normalization/engine.py` and create corresponding test files in `tests/test_normalization.py` with expected inputs/outputs.

### 1.4 — Backend Dev (45 minutes)
**Task: Define the Compliance Engine contract**

Sketch how rules are loaded and checked.

```python
# src/compliance/engine.py (pseudocode)

def load_framework_rules(framework_name: str) -> List[Rule]:
    """Load rules from YAML file for chosen framework."""
    pass

def evaluate_device(device_config: DeviceConfig, framework: str) -> ComplianceResult:
    """
    Check the normalized config against selected framework rules.
    Returns: detailed findings with pass/fail + severity + source lines.
    """
    pass

class ComplianceResult(BaseModel):
    device_id: str
    framework: str
    total_controls: int
    passed: int
    failed: int
    critical_count: int
    findings: List[Finding]  # Each finding traces back to source line

class Finding(BaseModel):
    control_id: str
    control_name: str
    status: str  # "pass" or "fail"
    severity: str  # "critical", "high", "medium", "low"
    source_line: int
    raw_config_line: str
    remediation_command: str
```

**Key design:** Every finding has a `source_line` and `raw_config_line` — this is your explainability (NFR2 from earlier docs).

**Deliverable:** Define these classes in `src/compliance/engine.py` and `src/schema/baseline.py`.

### 1.5 — Frontend Dev (45 minutes)
**Task: Sketch the three screens**

Use Streamlit pseudo-code to define the user flow. Don't build anything yet, just define the functions.

```python
# frontend/streamlit_app.py (pseudocode)

import streamlit as st

# Main app routing
def main():
    page = st.sidebar.radio("Select Page", ["Upload", "Training", "Results"])
    
    if page == "Upload":
        page_upload()
    elif page == "Training":
        page_training()
    elif page == "Results":
        page_results()

def page_upload():
    """
    Upload config file(s), display processing status.
    Should call ingestion.uploader.upload_file() → normalization.engine.normalize_config() → compliance.engine.evaluate_device()
    """
    pass

def page_training():
    """
    Show unmapped lines from the normalized config.
    User picks category for each line.
    Call training.loop.commit_mapping() on submit.
    Re-run normalization immediately to show the line is now understood.
    """
    pass

def page_results():
    """
    Show compliance findings in a table, provide download button for PDF report.
    Call reporting.pdf_generator.generate_report()
    """
    pass
```

**Deliverable:** Commit this skeleton to `frontend/streamlit_app.py`.

### 1.6 — Research Lead (Final 30 minutes)
**Task: Extract ~15 actual security controls and write them to YAML**

Pull the actual CIS benchmark rules for network devices. For MVP, pick ONE framework (CIS). Extract ~15 high-signal controls that are:
1. Common across multiple device types (firewalls, switches, routers).
2. Syntactically checkable from a config file.
3. Present in multiple frameworks (so the same control maps to CIS-1.1, NIST AC-3, STIG V-1234, etc., in the "full product" story).

**Example:**
```yaml
# data/frameworks/cis_benchmarks.yaml

- id: "CIS_1.1"
  name: "Ensure SSH Protocol Version 2 is enabled"
  description: "SSH version 2 is the secure and updated version."
  schema_path: "baseline.remote_access.ssh_version"
  operator: "=="
  expected_value: 2
  severity: "critical"
  remediation_template: "ssh_version"
  remediation_commands:
    cisco: "ip ssh version 2"
    juniper: "set system services ssh protocol-version v2"
    arista: "ip ssh server enabled"

- id: "CIS_1.2"
  name: "Ensure Telnet is disabled"
  description: "Telnet sends credentials in plain text over the network."
  schema_path: "baseline.remote_access.telnet_enabled"
  operator: "=="
  expected_value: false
  severity: "critical"
  remediation_template: "disable_telnet"
  remediation_commands:
    cisco: "no ip telnet server enable"
    juniper: "delete system services telnet"

# ... 13 more controls ...
```

**Deliverable:** Save to `data/frameworks/cis_benchmarks.yaml`. This file is your "rules table" that the compliance engine reads.

### End of Day 1 Sync (30 minutes)
**All team members together:**
- Architect walks through the schema one more time: "Here's what will flow through the system."
- Everyone confirms they understand what the other person's module needs to consume as input and produce as output.
- Architect creates the `tests/` files with stub test cases that will be filled in as you build.

**Deliverable by EOD:**
- [ ] Schema defined in `src/schema/baseline.py`
- [ ] Function stubs in `src/normalization/engine.py`, `src/compliance/engine.py`, `frontend/streamlit_app.py`
- [ ] CIS rules in `data/frameworks/cis_benchmarks.yaml`
- [ ] Repo structure created, all empty files in place

---

## DAY 2: Core Modules Built Separately (In Parallel)

**Duration:** ~6–8 hours (full day)

**Philosophy:** Three teams work in parallel because they're all building around the same schema locked on Day 1. Minimal integration yet.

### 2.1 — AI/NLP Dev (Full day task)
**Primary:** Build Tier 1 (Regex/Pattern Matching)

**What to code:**
1. Load vendor patterns from YAML:
```python
# src/normalization/patterns.py

import yaml
import re
from typing import Dict, List, Tuple, Optional

def load_vendor_patterns(vendor: str) -> Dict[str, List[dict]]:
    """Load regex patterns for a specific vendor from YAML."""
    with open(f"data/vendor_patterns/{vendor}_patterns.yaml") as f:
        return yaml.safe_load(f)

def match_line(line: str, patterns: Dict) -> Optional[Tuple[str, float]]:
    """
    Try to match a config line against known patterns.
    Returns: (schema_path, confidence) or None
    """
    for category, pattern_list in patterns.items():
        for pattern_dict in pattern_list:
            regex = pattern_dict['regex']
            schema_path = pattern_dict['schema_path']
            if re.search(regex, line, re.IGNORECASE):
                # Extract the value if pattern has a capture group
                match = re.search(regex, line)
                value = match.group(1) if match.groups() else None
                return (schema_path, value, 1.0)  # confidence 1.0 = exact match
    return None
```

2. Process a config line-by-line:
```python
# src/normalization/engine.py (tier 1 implementation)

def tier1_exact_match(line: str, vendor: str) -> Optional[Tuple[str, any, float]]:
    patterns = load_vendor_patterns(vendor)
    result = match_line(line, patterns)
    return result if result else None
```

3. Create sample pattern YAMLs for Cisco and Juniper:
```yaml
# data/vendor_patterns/cisco_patterns.yaml

remote_access:
  - pattern_name: "ssh_version"
    schema_path: "baseline.remote_access.ssh_version"
    regex: "ip ssh version (\\d+)"
    value_type: "int"
  
  - pattern_name: "telnet_disabled"
    schema_path: "baseline.remote_access.telnet_enabled"
    regex: "no ip telnet server"
    value: false

authentication:
  - pattern_name: "password_min_length"
    schema_path: "baseline.authentication.min_password_length"
    regex: "password min-length (\\d+)"
    value_type: "int"
```

4. Write unit tests:
```python
# tests/test_normalization.py

def test_tier1_cisco_ssh():
    line = "ip ssh version 2"
    result = tier1_exact_match(line, "cisco")
    assert result == ("baseline.remote_access.ssh_version", 2, 1.0)

def test_tier1_no_match():
    line = "set obscure random setting xyz"
    result = tier1_exact_match(line, "cisco")
    assert result is None
```

**Deliverable:**
- [ ] `src/normalization/patterns.py` — load and match logic
- [ ] `data/vendor_patterns/cisco_patterns.yaml` — Cisco patterns
- [ ] `data/vendor_patterns/juniper_patterns.yaml` — Juniper patterns
- [ ] `tests/test_normalization.py` — unit tests passing
- [ ] README section explaining how to add a new vendor's patterns (YAML-only, no code changes)

### 2.2 — Backend Dev (Full day task)
**Primary:** Build Compliance Engine (Rule Evaluation)

**What to code:**
1. Load framework rules:
```python
# src/compliance/framework_loader.py

import yaml
from typing import List, Dict

class Rule:
    def __init__(self, rule_dict: dict):
        self.id = rule_dict['id']
        self.name = rule_dict['name']
        self.schema_path = rule_dict['schema_path']
        self.operator = rule_dict['operator']  # "==", "!=", "contains", etc.
        self.expected_value = rule_dict['expected_value']
        self.severity = rule_dict['severity']
        self.remediation = rule_dict.get('remediation_commands', {})

def load_framework(framework_name: str) -> List[Rule]:
    """Load all rules from a framework YAML file."""
    with open(f"data/frameworks/{framework_name}.yaml") as f:
        rules_data = yaml.safe_load(f)
    return [Rule(r) for r in rules_data]
```

2. Implement rule evaluation:
```python
# src/compliance/engine.py

def get_nested_value(obj: dict, path: str):
    """Extract value from nested dict using dot notation. E.g., 'baseline.remote_access.ssh_version'"""
    keys = path.split('.')
    for key in keys:
        obj = obj.get(key, {})
    return obj

def evaluate_rule(device_config: dict, rule: Rule) -> Finding:
    """Check a single rule against device config."""
    actual_value = get_nested_value(device_config, rule.schema_path)
    
    # Get source line for provenance
    provenance = device_config.get('provenance', {}).get(rule.schema_path.split('.')[-1], {})
    source_line = provenance.get('source_line', -1)
    raw_line = provenance.get('raw', '')
    
    # Evaluate condition
    passed = False
    if rule.operator == "==":
        passed = actual_value == rule.expected_value
    elif rule.operator == "!=":
        passed = actual_value != rule.expected_value
    elif rule.operator == "contains":
        passed = rule.expected_value in str(actual_value)
    # ... more operators as needed ...
    
    return Finding(
        control_id=rule.id,
        control_name=rule.name,
        status="pass" if passed else "fail",
        severity=rule.severity,
        source_line=source_line,
        raw_config_line=raw_line,
        remediation_command=rule.remediation.get('default', 'N/A')
    )

def evaluate_device(device_config: dict, framework: str) -> ComplianceResult:
    """Evaluate all rules for a framework against a device config."""
    rules = load_framework(framework)
    findings = [evaluate_rule(device_config, rule) for rule in rules]
    
    passed_count = sum(1 for f in findings if f.status == "pass")
    failed_count = len(findings) - passed_count
    critical_count = sum(1 for f in findings if f.severity == "critical" and f.status == "fail")
    
    return ComplianceResult(
        device_id=device_config['device']['hostname'],
        framework=framework,
        total_controls=len(findings),
        passed=passed_count,
        failed=failed_count,
        critical_count=critical_count,
        findings=findings
    )
```

3. Write tests:
```python
# tests/test_compliance.py

def test_evaluate_ssh_version_pass():
    device_config = {
        "device": {"hostname": "test-router"},
        "baseline": {"remote_access": {"ssh_version": 2}},
        "provenance": {"ssh_version": {"source_line": 5, "raw": "ip ssh version 2"}}
    }
    result = evaluate_device(device_config, "cis_benchmarks")
    finding = [f for f in result.findings if f.control_id == "CIS_1.1"][0]
    assert finding.status == "pass"
    assert finding.source_line == 5
```

**Deliverable:**
- [ ] `src/compliance/framework_loader.py` — load rules
- [ ] `src/compliance/engine.py` — evaluate logic
- [ ] `tests/test_compliance.py` — unit tests passing
- [ ] Manual check: run against a simple device_config dict, confirm findings are correct

### 2.3 — Frontend Dev (Full day task)
**Primary:** Build the Upload & Processing Flow

**What to code:**
1. File upload handling:
```python
# src/ingestion/uploader.py

import os
from typing import Tuple

def guess_vendor_family(config_text: str) -> str:
    """
    Heuristically guess vendor from config text.
    Look for vendor-specific keywords, prompts, or markers.
    """
    text_upper = config_text.upper()
    
    if "INTERFACE GIGABITETHERNET" in text_upper or "ROUTER#" in text_upper:
        return "cisco"
    elif "SET SYSTEM" in text_upper or "set interfaces" in text_upper:
        return "juniper"
    elif "INTERFACE ETHERNET" in text_upper or "ABOOT" in text_upper:
        return "arista"
    else:
        return "unknown"

def process_upload(file_bytes: bytes, filename: str) -> str:
    """
    Receive uploaded file, decode, return text.
    """
    try:
        config_text = file_bytes.decode('utf-8')
        return config_text
    except UnicodeDecodeError:
        # Handle binary/non-UTF8 files
        try:
            config_text = file_bytes.decode('latin-1')
            return config_text
        except:
            return None
```

2. Build the Streamlit upload page:
```python
# frontend/pages/01_upload.py

import streamlit as st
import sys
sys.path.insert(0, '../')

from src.normalization.engine import normalize_config
from src.compliance.engine import evaluate_device
from src.ingestion.uploader import process_upload, guess_vendor_family

st.set_page_config(page_title="Upload Config", layout="wide")
st.title("Network Device Compliance Scanner")

uploaded_file = st.file_uploader("Upload device config file (.txt, .cfg, .conf)", type=["txt", "cfg", "conf"])

if uploaded_file:
    config_text = process_upload(uploaded_file.getvalue(), uploaded_file.name)
    vendor = guess_vendor_family(config_text)
    
    st.info(f"Detected vendor: **{vendor}**")
    
    if st.button("Scan & Normalize"):
        with st.spinner("Processing..."):
            device_config = normalize_config(config_text, vendor)
            result = evaluate_device(device_config, "cis_benchmarks")
            
            # Store in session state for other pages to access
            st.session_state.device_config = device_config
            st.session_state.compliance_result = result
            
            st.success("✓ Scan complete!")
            st.write(f"Device: {device_config['device']['hostname']}")
            st.write(f"Unmapped lines: {len(device_config['unmapped_lines'])}")
            
            if device_config['unmapped_lines']:
                st.warning(f"⚠️ {len(device_config['unmapped_lines'])} lines need manual review")
                if st.button("Go to Training"):
                    st.session_state.page = "training"
            else:
                st.success("✓ All lines understood!")
```

**Deliverable:**
- [ ] `src/ingestion/uploader.py` — file processing + vendor detection
- [ ] `frontend/pages/01_upload.py` — working upload interface
- [ ] Test with one of the sample configs from Day 1

### 2.4 — Architect (Coordination + Integration Planning)
**Primary:** Ensure the three teams' outputs can talk to each other

**What to do:**
1. Create test data directory with sample configs:
```
data/sample_configs/
├── cisco_switch.cfg    # A real or realistic Cisco config
├── juniper_firewall.cfg
└── unknown_device.cfg   # Will be used for the live training demo
```

2. Write a simple integration test:
```python
# tests/test_integration.py

from src.normalization.engine import normalize_config
from src.compliance.engine import evaluate_device

def test_end_to_end_cisco():
    with open("data/sample_configs/cisco_switch.cfg") as f:
        config_text = f.read()
    
    device_config = normalize_config(config_text, "cisco")
    result = evaluate_device(device_config, "cis_benchmarks")
    
    assert result.total_controls > 0
    assert result.passed + result.failed == result.total_controls
    assert len(result.findings) > 0
    for finding in result.findings:
        assert finding.source_line >= -1  # -1 means unmapped, that's OK
```

3. Create a simple CLI runner for testing:
```python
# tests/manual_test.py

import sys
sys.path.insert(0, '../')

from src.normalization.engine import normalize_config
from src.compliance.engine import evaluate_device
import json

if __name__ == "__main__":
    config_file = sys.argv[1]  # Pass config file as argument
    vendor = sys.argv[2] if len(sys.argv) > 2 else "cisco"
    
    with open(config_file) as f:
        config_text = f.read()
    
    device_config = normalize_config(config_text, vendor)
    result = evaluate_device(device_config, "cis_benchmarks")
    
    print("=== NORMALIZED CONFIG ===")
    print(json.dumps(device_config, indent=2))
    print("\n=== COMPLIANCE RESULTS ===")
    print(f"Device: {result.device_id}")
    print(f"Passed: {result.passed}/{result.total_controls}")
    print(f"Failed: {result.failed}/{result.total_controls}")
    print(f"Critical Failures: {result.critical_count}")
    print("\n=== FINDINGS ===")
    for finding in result.findings:
        print(f"{finding.control_id}: {finding.status} ({finding.severity})")
        if finding.status == "fail":
            print(f"  Fix: {finding.remediation_command}")
```

**End of Day 2 Sync (15 minutes):**
- Architect runs the integration test with Day 2 outputs.
- Confirm all three modules can pass data to each other correctly.
- Log any integration issues for Day 3 fix.

**Deliverable by EOD:**
- [ ] All three core modules have working implementations (even if not polished)
- [ ] Unit tests passing for each module
- [ ] Integration test passing
- [ ] Manual CLI test working with sample configs

---

## DAY 3: The Differentiator — Training Loop

**Duration:** ~6 hours

**Philosophy:** Everything before Day 3 is "just another compliance tool." The training loop is what makes this project unique. Get this right.

### 3.1 — AI/NLP Dev + Backend Dev (Pair Programming)
**Primary:** Build the Training Loop Logic

**Design:**
When normalization encounters unmapped lines, they're stored in `device_config['unmapped_lines']` as:
```python
{
    "line_no": 42,
    "raw": "set security zone dmz screen block-tcp",
    "status": "needs_training"
}
```

The training loop does:
1. **Present** unmapped lines to a human
2. **Collect** the human's categorization (which schema path does this line map to?)
3. **Extract & generalize** a pattern from the line (so *similar* lines are recognized next time)
4. **Persist** the mapping to the knowledge store
5. **Re-run normalization** on the same file immediately (so the demo shows the line flip from unmapped→mapped)

**Code:**
```python
# src/training/loop.py

import sqlite3
from typing import Tuple, Optional
from src.schema.baseline import DeviceConfig

class TrainingLoop:
    def __init__(self, db_path: str = "compliance.db"):
        self.db_path = db_path
    
    def save_mapping(self, vendor: str, raw_line: str, schema_path: str, 
                     created_by: str = "admin", confidence: float = 1.0) -> bool:
        """
        Persist a human-confirmed mapping.
        This is the "learning" step.
        """
        # Generalize the line to a regex pattern
        # (simple approach: escape special chars, replace specific values with regex wildcards)
        pattern = self._generalize_to_pattern(raw_line)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store in vendor_patterns table
        cursor.execute("""
            INSERT INTO vendor_patterns (vendor, raw_pattern, schema_path, confidence, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (vendor, pattern, schema_path, confidence, created_by))
        
        conn.commit()
        conn.close()
        return True
    
    def get_unmapped_lines(self, device_config: DeviceConfig) -> list:
        """Return the unmapped lines from a config."""
        return device_config.unmapped_lines
    
    def _generalize_to_pattern(self, line: str) -> str:
        """
        Convert a specific line into a regex pattern.
        E.g., "ip ssh version 2" → "ip ssh version (\\d+)"
        
        For MVP, use simple heuristics:
        - Numbers → (\d+)
        - Specific keywords stay as-is
        """
        import re
        # Replace numbers with regex wildcard
        pattern = re.sub(r'\d+', r'(\\d+)', line)
        return pattern

    def apply_learned_mapping(self, line: str, vendor: str) -> Optional[Tuple[str, float]]:
        """
        Check if this line matches a human-confirmed mapping.
        Used during normalization after training.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT schema_path, confidence FROM vendor_patterns
            WHERE vendor = ? ORDER BY created_at DESC
        """, (vendor,))
        
        patterns = cursor.fetchall()
        conn.close()
        
        for schema_path, confidence in patterns:
            # Try to match this line against the stored pattern
            import re
            # Reconstruct a simple regex from the pattern string
            # (In production, store the actual regex, not try to re-create it)
            if re.search(schema_path, line, re.IGNORECASE):
                return (schema_path, confidence)
        
        return None
```

2. Database schema for training:
```sql
-- database/schema.sql

CREATE TABLE IF NOT EXISTS vendor_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor TEXT NOT NULL,
    raw_pattern TEXT NOT NULL,
    schema_path TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hostname TEXT UNIQUE,
    vendor TEXT,
    os_version TEXT,
    serial_number TEXT,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scan_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER REFERENCES devices(id),
    framework TEXT,
    passed INT,
    failed INT,
    critical_count INT,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS compliance_findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_result_id INTEGER REFERENCES scan_results(id),
    control_id TEXT,
    status TEXT,  -- "pass" or "fail"
    severity TEXT,
    source_line INT,
    raw_config_line TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT,
    user TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

3. Initialize database on first run:
```python
# src/storage/db.py

import sqlite3
import os

def init_db(db_path: str = "compliance.db"):
    """Initialize database schema on first run."""
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read and execute schema.sql
        with open("database/schema.sql") as f:
            cursor.executescript(f.read())
        
        conn.commit()
        conn.close()
```

4. Modify normalization engine to use learned mappings:
```python
# src/normalization/engine.py (updated)

from src.training.loop import TrainingLoop

def normalize_config(raw_text: str, vendor_hint: str = None) -> DeviceConfig:
    """
    Main entry point. Try three tiers, using learned mappings from training loop.
    """
    training_loop = TrainingLoop()
    
    lines = raw_text.split('\n')
    normalized_values = {}
    unmapped_lines = []
    provenance = {}
    
    for line_no, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Try tier 1: exact pattern match (including learned patterns from training loop)
        result = tier1_exact_match(line, vendor_hint)
        if not result:
            # Try learned mapping
            result = training_loop.apply_learned_mapping(line, vendor_hint)
        
        if result:
            schema_path, value, confidence = result
            # Store normalized value
            set_nested_value(normalized_values, schema_path, value)
            set_nested_value(provenance, schema_path, {"source_line": line_no, "raw": line})
        else:
            # Try tier 2, tier 3, etc...
            # If still no match, add to unmapped
            unmapped_lines.append({
                "line_no": line_no,
                "raw": line,
                "status": "needs_training"
            })
    
    return DeviceConfig(
        device={...},
        baseline=normalized_values,
        unmapped_lines=unmapped_lines,
        provenance=provenance,
        metadata={...}
    )
```

### 3.2 — Frontend Dev
**Primary:** Build the Training Interface Screen

```python
# frontend/pages/02_training.py

import streamlit as st
import sys
sys.path.insert(0, '../')

from src.training.loop import TrainingLoop
from src.normalization.engine import normalize_config

st.set_page_config(page_title="Training Interface", layout="wide")
st.title("🎓 Train the AI — Map Unknown Lines")

if 'device_config' not in st.session_state:
    st.error("No config loaded. Go to Upload first.")
    st.stop()

device_config = st.session_state.device_config
unmapped = device_config['unmapped_lines']

if not unmapped:
    st.success("✓ All lines mapped! No training needed.")
    st.stop()

st.write(f"**{len(unmapped)} lines need training.** Help the AI understand them:")

training_loop = TrainingLoop()

# Get list of known schema paths for the dropdown
known_categories = [
    "baseline.remote_access.ssh_version",
    "baseline.remote_access.telnet_enabled",
    "baseline.authentication.password_encryption",
    "baseline.authentication.aaa_enabled",
    "baseline.logging.admin_access_logging",
    "baseline.access_control.default_deny_present",
    # ... more categories from the schema ...
]

for idx, unmapped_line in enumerate(unmapped):
    st.divider()
    st.write(f"**Line {unmapped_line['line_no']}:** `{unmapped_line['raw']}`")
    
    # Show context (surrounding lines if available)
    # ...
    
    # User picks which category this line belongs to
    category = st.selectbox(
        "What does this line control?",
        options=known_categories + ["[NEW CATEGORY]"],
        key=f"category_{idx}"
    )
    
    if category == "[NEW CATEGORY]":
        custom_category = st.text_input("Enter new category path:", key=f"new_cat_{idx}")
        category = custom_category if custom_category else category
    
    # Submit button
    if st.button(f"Learn line {idx}", key=f"submit_{idx}"):
        success = training_loop.save_mapping(
            vendor=device_config['device']['vendor'],
            raw_line=unmapped_line['raw'],
            schema_path=category,
            created_by="user"  # In production, get actual user from auth
        )
        
        if success:
            st.success(f"✓ Learned! Re-running normalization...")
            
            # Re-normalize with the new mapping
            raw_text = st.session_state.raw_config_text  # Need to store this earlier
            device_config = normalize_config(raw_text, device_config['device']['vendor'])
            st.session_state.device_config = device_config
            
            st.rerun()  # Refresh page to show updated state

st.write("---")
if st.button("✓ Done Training — Show Results"):
    st.switch_page("pages/03_results.py")
```

### 3.3 — Research Lead
**Task:** Build the PDF report generator skeleton

```python
# src/reporting/pdf_generator.py

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime

def generate_report(device_config: dict, compliance_result: dict, output_path: str):
    """
    Generate a PDF report from compliance findings.
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title page
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30
    )
    story.append(Paragraph("Network Device Compliance Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Device info
    story.append(Paragraph(f"<b>Device:</b> {device_config['device']['hostname']}", styles['Normal']))
    story.append(Paragraph(f"<b>Vendor:</b> {device_config['device']['vendor']}", styles['Normal']))
    story.append(Paragraph(f"<b>OS Version:</b> {device_config['device']['os_version']}", styles['Normal']))
    story.append(Paragraph(f"<b>Scanned:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Summary
    story.append(Paragraph("<b>Compliance Summary</b>", styles['Heading2']))
    summary_data = [
        ['Framework', compliance_result['framework']],
        ['Total Controls', str(compliance_result['total_controls'])],
        ['Passed', str(compliance_result['passed'])],
        ['Failed', str(compliance_result['failed'])],
        ['Critical', str(compliance_result['critical_count'])]
    ]
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Findings table
    story.append(Paragraph("<b>Detailed Findings</b>", styles['Heading2']))
    findings_data = [['Control ID', 'Status', 'Severity', 'Source Line', 'Remediation']]
    for finding in compliance_result['findings']:
        status_color = 'green' if finding['status'] == 'pass' else 'red'
        findings_data.append([
            finding['control_id'],
            f"<font color={status_color}>{finding['status'].upper()}</font>",
            finding['severity'],
            str(finding['source_line']),
            finding['remediation_command'][:30] + "..." if len(finding['remediation_command']) > 30 else finding['remediation_command']
        ])
    
    findings_table = Table(findings_data, colWidths=[1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 2*inch])
    findings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(findings_table)
    story.append(PageBreak())
    
    # Remediation commands appendix
    story.append(Paragraph("<b>Remediation Commands</b>", styles['Heading2']))
    for finding in compliance_result['findings']:
        if finding['status'] == 'fail':
            story.append(Paragraph(f"<b>{finding['control_id']}</b>", styles['Normal']))
            story.append(Paragraph(f"<font face='Courier'>{finding['remediation_command']}</font>", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(story)
```

**Deliverable by EOD of Day 3:**
- [ ] Training loop persisting mappings to DB
- [ ] Learned mappings being used in re-normalization
- [ ] Training interface screen in Streamlit
- [ ] PDF report generator skeleton (even if not perfect visually)
- [ ] Full end-to-end test: upload → see unmapped lines → train on a line → re-run → line is now mapped

---

## DAY 4: Integration, Testing, Polish

**Duration:** ~6–8 hours

**Philosophy:** Everything works individually; now connect everything and fix what breaks.

### 4.1 — Architect + All (Full day)
**Primary:** End-to-end pipeline integration + bug fixes

**Checklist:**
- [ ] Upload a Cisco config → normalize → check rules → generate report ✓
- [ ] Upload an unknown vendor config → see unmapped lines ✓
- [ ] Train on 2–3 unmapped lines → re-run → confirm they're now mapped ✓
- [ ] PDF report downloads and opens correctly ✓
- [ ] All unit tests pass ✓
- [ ] Manual testing with all three sample configs (cisco, juniper, unknown) ✓

**Common issues to debug:**
1. **Unmapped lines not flowing to training interface** — check that `device_config['unmapped_lines']` is being populated.
2. **Learned mapping not being re-applied** — check that `apply_learned_mapping()` is being called in the re-normalize path.
3. **PDF generation failing** — check ReportLab dependencies, test PDF creation in isolation first.
4. **Session state issues in Streamlit** — ensure `st.session_state` is being used correctly to pass data between pages.

### 4.2 — Backend Dev
**Task:** Build PDF generation fully + test with real compliance results

```python
# tests/test_reporting.py

from src.reporting.pdf_generator import generate_report

def test_pdf_generation():
    device_config = {
        "device": {
            "hostname": "test-device",
            "vendor": "cisco",
            "os_version": "15.2",
            "serial_number": "ABC123"
        },
        "baseline": {...},
        "unmapped_lines": [],
        "provenance": {...},
        "metadata": {"scan_timestamp": "2025-01-15T10:00:00"}
    }
    
    compliance_result = {
        "device_id": "test-device",
        "framework": "cis_benchmarks",
        "total_controls": 5,
        "passed": 3,
        "failed": 2,
        "critical_count": 1,
        "findings": [...]
    }
    
    output_path = "/tmp/test_report.pdf"
    generate_report(device_config, compliance_result, output_path)
    
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0
```

### 4.3 — Frontend Dev
**Task:** Build the Results page + download button

```python
# frontend/pages/03_results.py

import streamlit as st
import sys
sys.path.insert(0, '../')

from src.reporting.pdf_generator import generate_report
import tempfile
import os

st.set_page_config(page_title="Compliance Results", layout="wide")
st.title("📊 Compliance Results")

if 'compliance_result' not in st.session_state:
    st.error("No compliance results. Go to Upload first.")
    st.stop()

result = st.session_state.compliance_result
device_config = st.session_state.device_config

# Display summary
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Controls", result.total_controls)
with col2:
    st.metric("Passed", result.passed, delta="+", delta_color="green")
with col3:
    st.metric("Failed", result.failed, delta="-", delta_color="red")
with col4:
    st.metric("Critical", result.critical_count, delta="-", delta_color="red")

st.divider()

# Findings table
st.write("### Detailed Findings")
findings_df = pd.DataFrame([
    {
        "Control ID": f.control_id,
        "Status": f.status,
        "Severity": f.severity,
        "Source Line": f.source_line,
        "Remediation": f.remediation_command
    }
    for f in result.findings
])
st.dataframe(findings_df, use_container_width=True)

st.divider()

# Download PDF button
st.write("### Download Report")
with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
    generate_report(device_config.dict(), result.dict(), tmp.name)
    with open(tmp.name, "rb") as f:
        pdf_bytes = f.read()
    
    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_bytes,
        file_name=f"{device_config['device']['hostname']}_compliance_report.pdf",
        mime="application/pdf"
    )
    
    os.unlink(tmp.name)
```

### 4.4 — Research Lead
**Task:** Finalize demo script + architecture document draft

**Demo Script (~2 minutes):**
```
[ON SCREEN: Blank dashboard]

"Hi, thanks for having us. In one minute, we're going to show you what makes our product different.

[CLICK UPLOAD]

We're a team building a network compliance scanner. The problem: security teams have devices from Cisco, 
Juniper, Palo Alto, dozens of vendors. Each vendor speaks a different 'language' in their config files.

[UPLOAD cisco_switch.cfg]

We upload a Cisco switch config...

[WAIT FOR PROCESSING]

It normalizes the config into a standard format, checks it against security rules... and in seconds, we know 
what's compliant and what's not.

But here's the part that's different:

[UPLOAD unknown_device.cfg]

We upload a config from a device brand we've literally never seen before.

[SHOW UNMAPPED LINES]

Instead of guessing wrong or crashing, our system says 'I don't understand these lines yet' and asks us to teach it.

[CLICK ON TRAINING INTERFACE]

Here, we just pick what each line means. This one sets security zones... this one sets a timeout...

[SUBMIT]

And that's it. Watch:

[RE-RUN NORMALIZATION]

Now it understands the line. The AI learned something new. And next time a config from this brand comes in, 
it won't need to ask again. That's what makes this product scale.

[SHOW PDF]

We generate a report that security teams can hand to their bosses: here's what passed, here's what failed, 
and here's exactly how to fix it.

That's our product."

[TOTAL TIME: ~90 seconds]
```

### 4.5 — All Team
**Task:** Write up README with setup instructions

```markdown
# Network Device Compliance Engine

## Quick Start

### Prerequisites
- Python 3.11+
- pip / virtualenv

### Installation

1. Clone the repo:
   git clone <repo-url>
   cd compliance-engine

2. Create virtual env:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Initialize database:
   python -c "from src.storage.db import init_db; init_db()"

### Running the Application

1. Start the Streamlit app:
   streamlit run frontend/streamlit_app.py

2. Navigate to http://localhost:8501 in your browser

3. Upload a device config file and watch it scan!

### Running Tests

   pytest tests/

### Adding a New Vendor

1. Create `data/vendor_patterns/[vendor_name]_patterns.yaml`
2. Add regex patterns mapping vendor commands to schema paths
3. No code changes needed!

### Supported Frameworks

- CIS Benchmarks (MVP)
- NIST SP 800-53 (Roadmap)
- DISA STIG (Roadmap)
- ISO/IEC 27001 (Roadmap)

```

**Deliverable by EOD:**
- [ ] Full end-to-end pipeline working with all three sample configs
- [ ] All tests passing
- [ ] PDF reports generating and downloadable
- [ ] Demo script finalized
- [ ] README ready for handout

---

## DAY 5: Final Polish, Rehearsal, Submission

**Duration:** ~4–5 hours (morning/early afternoon for polish, afternoon/evening for rehearsal)

### 5.1 — Research Lead + Architect (2 hours)
**Task:** Finalize the 5-slide PPT

**Slide structure:**
1. **Problem** — (30 sec) Different vendors, same rules, no unified tool
2. **Solution** — (30 sec) Our vendor-agnostic, AI-learning platform (architecture diagram)
3. **Technology** — (1 min) Three-tier normalization (regex → embeddings → LLM with human confirmation)
4. **The Demo** — (1 min) Live show-and-tell of the training loop
5. **Impact + Roadmap** — (1 min) Market opportunity, Phase 1/2/3 roadmap

**Slide 3 visual worth spending time on:**
```
TIER 1 (Fast & Cheap)       TIER 2 (Medium)            TIER 3 (Expensive & Careful)
Regex Pattern Match    →    Embedding Similarity   →   LLM Suggestion + Human Review
(known vendors)             (similar patterns)         (genuinely new things)
80% of cases           →    15% of cases          →    5% of cases
Confidence: 1.0        →    Confidence: 0.7–0.9  →    Confidence: Pending Human
```

### 5.2 — Frontend Dev (1 hour)
**Task:** Record the 2-minute demo video

- Script: Use the demo script from Day 4 section 4.4
- Setup: Clean desktop, terminal/screen cleared, Streamlit app open, sample configs ready
- Record with OBS or QuickTime
- Edit lightly (maybe speed up waiting/processing parts)
- Upload to a shared Google Drive / GitHub release page

### 5.3 — Architect (1 hour)
**Task:** Finalize Architecture Document (2 pages)

**Page 1:**
- High-level architecture diagram (5 boxes: Ingestion → Normalization → Compliance → Training Loop → Reporting)
- Data flow narrative (1 config file's journey through the system)

**Page 2:**
- Tech stack table (see earlier tech-stack-detailed.md)
- Design decisions & tradeoffs (why regex-first, why human-confirmed learning, why SQLite for MVP)

### 5.4 — All Team (2 hours)
**Task:** Full rehearsal of the live demo + Q&A

**Run through:**
1. Start from a blank screen (don't have things pre-loaded).
2. Upload Cisco config → show normalization → show compliance findings → show PDF.
3. Upload unknown vendor config → show unmapped lines → train on 2 lines → re-run → show lines are now mapped.
4. Answer the 6 common questions from the lecture notes Part 5.

**Rehearsal checklist:**
- [ ] All URLs/file paths work (no "file not found" during demo)
- [ ] Network latency isn't killing the demo (if using Claude API, test latency; if slow, consider removing Tier 3 from the live demo)
- [ ] PDF downloads without errors
- [ ] Demo takes <2 minutes total
- [ ] All team members know what to say at each step
- [ ] Someone is designated as the primary speaker; others are ready to field Q&A

### 5.5 — All Team (Final 30 minutes)
**Task:** Final submission checklist

Before you hit "submit," verify:

- [ ] **Source Code** — All files committed to GitHub with a clean README
  ```
  - Check: `git log` shows meaningful commits (not "final fix" on every line)
  - Check: No API keys or credentials in the repo
  - Check: requirements.txt has all dependencies
  ```

- [ ] **README** — Has setup instructions that actually work
  ```
  - Verify: Run the exact commands from the README on a fresh clone
  ```

- [ ] **Architecture Document** — 2 pages, explains the design
  ```
  - Page 1: Diagram + data flow
  - Page 2: Tech stack + design decisions
  ```

- [ ] **Demo Video** — <2 minutes, shows the live training loop working
  ```
  - Resolution: 1080p+
  - Audio: Clear
  - Speed: Normal (don't skip important steps)
  ```

- [ ] **Technical Presentation** — 5 slides covering problem/solution/tech/demo/roadmap
  ```
  - Use the 5-slide structure above
  - Practice delivering in 5 minutes flat
  ```

---

## RISK MITIGATION & CONTINGENCIES

**If X fails on demo day, do Y:**

| Risk | Mitigation |
|---|---|
| **Streamlit app is slow** | Pre-load sample configs; don't wait for live API calls during demo |
| **Claude API timeouts (Tier 3)** | Have the demo pre-recorded as backup; use regex+embedding (Tier 1+2) only for live demo |
| **Unmapped lines aren't flowing to training screen** | Fall back to showing a static training screen with pre-recorded results |
| **PDF doesn't generate** | Have a pre-generated PDF ready to download as a fallback; show it in the PDF viewer |
| **Teammate can't make it demo day** | Ensure every team member can explain every part of the project (not just their own module) |
| **Judge asks about scaling** | Have a slide ready with: "Same architecture (Streamlit → FastAPI, SQLite → PostgreSQL, single-machine → Kubernetes)" |

---

## Final Checklist Before Hitting "Submit"

- [ ] Everyone can explain the problem in one sentence
- [ ] Everyone can explain the three-tier AI cascade
- [ ] Everyone can explain why this is different from "just use ChatGPT"
- [ ] Everyone can trace a config file through the whole pipeline
- [ ] Someone owns each of the 5 deliverables (code, readme, architecture, video, PPT)
- [ ] Demo video recorded and ready to play back
- [ ] Slides reviewed by at least 2 people
- [ ] All 5 team members have rehearsed the pitch together at least twice
- [ ] Everyone's contact info is in the README
- [ ] Code is on GitHub with a public link ready to share

---

## On Demo Day

**60 minutes before:**
- Arrive early, test WiFi/AV setup
- Load the demo video on a USB stick as backup
- Have PDFs of your slides printed (judges sometimes prefer paper)
- Do a dry run of the live demo one more time

**During presentation:**
- Speak from the narrative (lecture notes Part 2), not from slides
- One person presents, others are ready for Q&A
- If something breaks, acknowledge it calmly and move to the next part (judges respect honesty more than pretending it didn't happen)
- Answer the 6 common questions (from lecture notes Part 5) with confidence — you've heard them before

**After presentation:**
- Thank judges, hand over USB/GitHub link
- Offer to stay and answer technical deep-dives (show you know this system cold)

---

**That's it. You have everything you need. Go build something great.**
