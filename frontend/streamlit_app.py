"""PRISM Streamlit dashboard entry point."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from frontend import ui
from frontend.findings import priority_findings, render_finding_row
from src.compliance.engine import evaluate_device


ui.configure_page("Overview")
ui.render_sidebar("overview")

config = st.session_state.get("device_config")
ui.page_header(
    eyebrow="Network compliance",
    title="Overview",
    description="Compliance posture and pipeline status for the active configuration.",
    action=None if config is None else ("Upload a different configuration", "pages/01_Upload.py"),
)

if config is None:
    ui.empty_state(
        title="No configuration loaded",
        description=(
            "PRISM converts a vendor configuration into a vendor-neutral security baseline, "
            "then evaluates it against CIS benchmark controls. Upload a configuration to begin."
        ),
        cta_label="Upload configuration",
        cta_page="pages/01_Upload.py",
    )
else:
    result = evaluate_device(config.model_dump(), "cis_benchmarks")
    st.session_state["compliance_result"] = result
    total = result.get("total_controls", 0)
    passed = result.get("passed", 0)
    critical = result.get("critical_count", 0)
    needs_training = len(config.unmapped_lines)
    score_pct = (passed / total * 100) if total else 0.0
    score_tone = "pass" if score_pct >= 80 else "medium" if score_pct >= 50 else "critical"

    ui.metric_strip(
        [
            {"label": "Compliance score", "value": f"{score_pct:.0f}%", "detail": f"{passed} of {total} controls passed", "tone": score_tone},
            {"label": "Critical findings", "value": critical, "detail": "Require immediate attention" if critical else "None detected", "tone": "critical" if critical else "pass"},
            {"label": "Needs training", "value": needs_training, "detail": "Unmapped configuration lines" if needs_training else "All lines mapped", "tone": "medium" if needs_training else "pass"},
            {"label": "Mapped fields", "value": len(config.provenance), "detail": f"{str(st.session_state.get('vendor', 'unknown')).title()} · {st.session_state.get('filename', '')}", "tone": "neutral"},
        ]
    )

    st.write("")
    ui.pipeline_stepper([("Ingest", "done"), ("Normalize", "done"), ("Review", "active" if needs_training else "done"), ("Evaluate", "done")])
    st.write("")

    left, right = st.columns([1.6, 1])
    with left:
        with st.container(border=True):
            ui.panel_title("Findings requiring attention", "Highest-priority results from the latest evaluation.")
            records, columns = priority_findings(result.get("findings", []), limit=6)
            if not records:
                st.markdown('<div class="prism-kv">No findings were returned by the evaluation.</div>', unsafe_allow_html=True)
            else:
                for record in records:
                    render_finding_row(record, columns)
            st.write("")
            st.page_link("pages/03_Results.py", label="View full results")
    with right:
        with st.container(border=True):
            ui.panel_title("Configuration snapshot")
            st.markdown(
                f'<div class="prism-kv">File · <b>{ui.escape_html(st.session_state.get("filename", "—"))}</b></div>'
                f'<div class="prism-kv">Vendor · <b>{ui.escape_html(str(st.session_state.get("vendor", "unknown")).title())}</b></div>'
                f'<div class="prism-kv">Mapped fields · <b>{len(config.provenance)}</b></div>'
                f'<div class="prism-kv">Unmapped lines · <b>{needs_training}</b></div>',
                unsafe_allow_html=True,
            )
            st.write("")
            if needs_training:
                st.page_link("pages/02_Training.py", label="Review unmapped lines")
            else:
                st.page_link("pages/01_Upload.py", label="Upload another configuration")
