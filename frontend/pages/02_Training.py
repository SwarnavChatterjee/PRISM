import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from frontend import ui
from src.normalization.engine import normalize_config
from src.training.loop import TrainingLoop


ui.configure_page("Training")
ui.render_sidebar("training")
ui.page_header(
    eyebrow="Step 2 of 2 · Human-in-the-loop",
    title="Training review",
    description=(
        "Configuration lines PRISM could not map to the security baseline. "
        "Confirmed mappings are stored locally and reused automatically for this vendor."
    ),
)

config = st.session_state.get("device_config")
raw_config = st.session_state.get("raw_config")
vendor = st.session_state.get("vendor", "unknown")

if config is None or raw_config is None:
    ui.empty_state(
        title="No configuration to review",
        description="Upload and normalize a configuration before reviewing unmapped lines.",
        cta_label="Go to upload",
        cta_page="pages/01_Upload.py",
    )
    st.stop()

unmapped = config.unmapped_lines
if not unmapped:
    ui.metric_strip([{"label": "Lines needing review", "value": 0, "detail": "All lines mapped", "tone": "pass"}])
    st.write("")
    st.success("No unmapped lines need training. This configuration is fully mapped to the baseline schema.")
    st.page_link("pages/03_Results.py", label="View compliance results")
else:
    ui.metric_strip([{"label": "Lines needing review", "value": len(unmapped), "detail": "Unrecognized by the current schema", "tone": "medium"}])
    st.write("")
    st.markdown(
        '<div class="prism-panel-caption">An unmapped line was not matched to a known baseline field, so it is excluded from compliance evaluation until you confirm what it means. Select the canonical field it corresponds to, optionally provide its value, and confirm.</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    schema_options = [
        "baseline.remote_access.ssh_version",
        "baseline.remote_access.telnet_enabled",
        "baseline.remote_access.http_management_enabled",
        "baseline.authentication.aaa_enabled",
        "baseline.authentication.min_password_length",
        "baseline.logging.syslog_configured",
    ]
    loop = TrainingLoop()
    for item in unmapped:
        row_key = item["line_no"]
        with st.container(border=True):
            st.markdown(f'<span class="prism-mono-chip">Line {row_key}</span>', unsafe_allow_html=True)
            st.code(item["raw"], language="text")
            field_col, value_col, action_col = st.columns([2, 2, 1])
            with field_col:
                selected_path = st.selectbox("Canonical field", schema_options, key=f"path_{row_key}")
            with value_col:
                mapped_value = st.text_input("Mapped value", key=f"value_{row_key}", placeholder="Defaults to true")
            with action_col:
                st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
                confirm_clicked = st.button("Confirm", key=f"confirm_{row_key}", use_container_width=True)
            if confirm_clicked:
                value = mapped_value if mapped_value else True
                if mapped_value and mapped_value.isdigit():
                    value = int(mapped_value)
                loop.save_mapping(vendor, item["raw"], selected_path, mapped_value=value)
                st.session_state["device_config"] = normalize_config(raw_config, vendor, db_path="compliance.db")
                st.rerun()
