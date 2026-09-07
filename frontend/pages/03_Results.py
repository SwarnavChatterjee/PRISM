import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from frontend import ui
from frontend.findings import detect_columns, style_findings
from src.compliance.engine import evaluate_device


ui.configure_page("Results")
ui.render_sidebar("results")
ui.page_header(
    eyebrow="Evaluation",
    title="Compliance results",
    description="Findings from evaluating the normalized baseline against CIS benchmark controls.",
)

config = st.session_state.get("device_config")
if config is None:
    ui.empty_state(
        title="No results yet",
        description="Upload and normalize a configuration to generate a compliance evaluation.",
        cta_label="Go to upload",
        cta_page="pages/01_Upload.py",
    )
    st.stop()

result = evaluate_device(config.model_dump(), "cis_benchmarks")
st.session_state["compliance_result"] = result
total = result["total_controls"]
passed = result["passed"]
failed = result["failed"]
critical = result["critical_count"]
score_pct = (passed / total * 100) if total else 0.0
score_tone = "pass" if score_pct >= 80 else "medium" if score_pct >= 50 else "critical"

ui.metric_strip(
    [
        {"label": "Total controls", "value": total, "tone": "neutral"},
        {"label": "Passed", "value": passed, "tone": "pass"},
        {"label": "Failed", "value": failed, "tone": "critical" if failed else "pass"},
        {"label": "Critical", "value": critical, "tone": "critical" if critical else "pass"},
    ]
)
st.write("")
st.markdown(
    f'<div class="prism-kv">Overall compliance score · <b style="color:{ui.TONE_FG[score_tone]}">{score_pct:.0f}%</b></div>',
    unsafe_allow_html=True,
)
st.progress(min(max(score_pct / 100, 0.0), 1.0))
st.write("")

findings = result.get("findings", [])
df = pd.DataFrame(findings)
with st.container(border=True):
    ui.panel_title("Findings", f"{len(df)} result{'s' if len(df) != 1 else ''} from this evaluation.")
    if df.empty:
        st.markdown('<div class="prism-kv">No findings were returned by the evaluation.</div>', unsafe_allow_html=True)
    else:
        columns = detect_columns(list(df.columns))
        active_filters = [column for column in (columns["status"], columns["severity"]) if column]
        filtered = df
        if active_filters:
            filter_cols = st.columns(len(active_filters))
            for widget, column in zip(filter_cols, active_filters):
                options = ["All"] + sorted(df[column].dropna().astype(str).unique().tolist())
                choice = widget.selectbox(column.replace("_", " ").title(), options, key=f"filter_{column}")
                if choice != "All":
                    filtered = filtered[filtered[column].astype(str) == choice]
        st.dataframe(style_findings(filtered), use_container_width=True, hide_index=True)

st.write("")
st.download_button(
    "Download results (JSON)",
    data=json.dumps(result, indent=2),
    file_name="prism-compliance-results.json",
    mime="application/json",
)
