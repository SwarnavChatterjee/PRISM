import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from frontend import ui
from src.compliance.engine import evaluate_device
from src.ingestion.uploader import decode_config, detect_vendor
from src.normalization.engine import normalize_config


ui.configure_page("Configuration analysis")
ui.render_sidebar("upload")
ui.page_header(
    eyebrow="Step 1 of 2 · Ingestion and normalization",
    title="Configuration analysis",
    description="Upload a vendor configuration and convert it into PRISM's vendor-neutral security baseline.",
)

left, right = st.columns([1.45, 1])
with left:
    with st.container(border=True):
        ui.panel_title("Upload configuration", "Supported text formats: .cfg, .conf, .config, .txt, and .set.")
        uploaded = st.file_uploader("Choose a configuration file", type=["cfg", "conf", "config", "txt", "set"], label_visibility="collapsed")
        if uploaded is not None:
            try:
                raw_text = decode_config(uploaded.name, uploaded.getvalue())
                detected, confidence = detect_vendor(raw_text)
                choices = ["cisco", "juniper", "unknown"]
                default = choices.index(detected) if detected in choices else 2
                vendor = st.selectbox("Vendor", choices, index=default)
                if detected != "unknown":
                    st.caption(f"Detected {detected.title()} with {confidence:.0%} confidence. Verify before proceeding.")
                if st.button("Normalize configuration", type="primary", use_container_width=True):
                    config = normalize_config(raw_text, vendor)
                    st.session_state.update(
                        raw_config=raw_text,
                        filename=uploaded.name,
                        vendor=vendor,
                        device_config=config,
                        compliance_result=evaluate_device(config.model_dump(), "cis_benchmarks"),
                    )
                    st.success("Configuration normalized successfully.")
                    st.page_link("pages/02_Training.py", label="Continue to training review")
            except ValueError as exc:
                st.error(str(exc))
with right:
    with st.container(border=True):
        ui.panel_title("What happens next")
        ui.pipeline_stepper([("Upload", "active"), ("Normalize", "active"), ("Review", "neutral"), ("Evaluate", "neutral")])
        st.write("")
        st.markdown(
            '<div class="prism-panel-caption">PRISM first uses deterministic YAML patterns. Lines it cannot map are sent to human review instead of being silently treated as compliant.</div>',
            unsafe_allow_html=True,
        )

if "device_config" in st.session_state:
    config = st.session_state["device_config"]
    st.write("")
    ui.metric_strip(
        [
            {"label": "Mapped fields", "value": len(config.provenance), "detail": "Canonical fields identified", "tone": "pass"},
            {"label": "Needs training", "value": len(config.unmapped_lines), "detail": "Lines awaiting confirmation", "tone": "medium" if config.unmapped_lines else "pass"},
        ]
    )
    with st.expander("Configuration preview"):
        st.code(st.session_state.get("raw_config", "")[:12000], language="text")
