"""Shared visual language and navigation helpers for the PRISM UI."""

from __future__ import annotations

from html import escape
from typing import Any, Iterable

import streamlit as st


TONE_FG = {
    "pass": "#55d187",
    "medium": "#e6b85c",
    "critical": "#ff7b72",
    "neutral": "#c9d1d9",
}


def configure_page(title: str) -> None:
    st.set_page_config(page_title=f"PRISM · {title}", page_icon="🛡️", layout="wide")
    st.markdown(
        """
        <style>
        :root { --bg:#0a0e13; --panel:#111820; --line:#26313d; --muted:#8b98a7; --text:#edf3f8; --blue:#63a4ff; }
        .stApp { background:var(--bg); color:var(--text); }
        .block-container { max-width:1440px; padding:2.2rem 3rem 4rem; }
        section[data-testid="stSidebar"] { background:#080c11; border-right:1px solid var(--line); }
        section[data-testid="stSidebar"] .block-container { padding:1.4rem 1.1rem; }
        .prism-brand { font-size:1.35rem; font-weight:800; letter-spacing:-.04em; }
        .prism-brand-accent { color:var(--blue); }
        .prism-eyebrow { color:var(--blue); font-size:.74rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; margin-bottom:.55rem; }
        .prism-title { font-size:2.25rem; line-height:1.08; font-weight:760; letter-spacing:-.045em; margin:0; }
        .prism-description { color:var(--muted); font-size:1rem; max-width:760px; margin-top:.65rem; line-height:1.55; }
        .prism-panel-caption { color:var(--muted); font-size:.88rem; line-height:1.55; }
        .prism-kv { color:var(--muted); font-size:.9rem; line-height:1.9; }
        .prism-kv b { color:var(--text); font-weight:600; }
        .prism-mono-chip { display:inline-block; color:#9ecbff; background:#152438; border:1px solid #294969; border-radius:5px; padding:.22rem .48rem; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.72rem; }
        .prism-metric { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:1rem 1.1rem; min-height:116px; }
        .prism-metric-label { color:var(--muted); font-size:.72rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
        .prism-metric-value { color:var(--text); font-size:1.8rem; font-weight:750; margin-top:.35rem; }
        .prism-metric-detail { color:var(--muted); font-size:.78rem; margin-top:.25rem; }
        .prism-metric.pass .prism-metric-value { color:#55d187; }
        .prism-metric.medium .prism-metric-value { color:#e6b85c; }
        .prism-metric.critical .prism-metric-value { color:#ff7b72; }
        .prism-pipeline { display:flex; gap:.55rem; flex-wrap:wrap; }
        .prism-step { color:var(--muted); border:1px solid var(--line); border-radius:999px; padding:.42rem .72rem; font-size:.78rem; }
        .prism-step.done { color:#55d187; border-color:#245b3e; background:#11251b; }
        .prism-step.active { color:#9ecbff; border-color:#315e8d; background:#122237; }
        .stButton > button, .stLinkButton > a { border-radius:8px; font-weight:650; }
        [data-testid="stFileUploader"] { background:#0f151c; border:1px dashed #3b4b5c; border-radius:12px; padding:.7rem; }
        footer { visibility:hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(active: str) -> None:
    with st.sidebar:
        st.markdown('<div class="prism-brand">PR<span class="prism-brand-accent">I</span>SM</div>', unsafe_allow_html=True)
        st.caption("Network compliance intelligence")
        st.divider()
        st.markdown("**Workspace**")
        pages = {
            "overview": ("Overview", "streamlit_app.py"),
            "upload": ("Configuration analysis", "pages/01_Upload.py"),
            "training": ("Training review", "pages/02_Training.py"),
            "results": ("Compliance results", "pages/03_Results.py"),
        }
        for key, (label, path) in pages.items():
            if key == active:
                st.markdown(f"**● {label}**")
            else:
                st.page_link(path, label=label)
        st.divider()
        st.markdown("**Engine status**")
        st.markdown('<span class="prism-mono-chip">● Tier 1 online</span>', unsafe_allow_html=True)
        st.caption("Exact YAML pattern matching")
        st.divider()
        st.caption("MVP · Human-confirmed intelligence")


def page_header(eyebrow: str, title: str, description: str, action: tuple[str, str] | None = None) -> None:
    left, right = st.columns([5, 1])
    with left:
        st.markdown(f'<div class="prism-eyebrow">{escape(eyebrow)}</div>', unsafe_allow_html=True)
        st.markdown(f'<h1 class="prism-title">{escape(title)}</h1>', unsafe_allow_html=True)
        st.markdown(f'<div class="prism-description">{escape(description)}</div>', unsafe_allow_html=True)
    with right:
        if action:
            st.page_link(action[1], label=action[0], use_container_width=True)
    st.write("")


def empty_state(title: str, description: str, cta_label: str, cta_page: str) -> None:
    with st.container(border=True):
        st.markdown(f"### {escape(title)}")
        st.markdown(f'<div class="prism-panel-caption">{escape(description)}</div>', unsafe_allow_html=True)
        st.write("")
        st.page_link(cta_page, label=cta_label, use_container_width=False)


def metric_strip(metrics: Iterable[dict[str, Any]]) -> None:
    items = list(metrics)
    columns = st.columns(len(items))
    for column, metric in zip(columns, items):
        tone = metric.get("tone", "neutral")
        with column:
            st.markdown(
                f'<div class="prism-metric {escape(tone)}">'
                f'<div class="prism-metric-label">{escape(str(metric.get("label", "")))}</div>'
                f'<div class="prism-metric-value">{escape(str(metric.get("value", "—")))}</div>'
                f'<div class="prism-metric-detail">{escape(str(metric.get("detail", "")))}</div></div>',
                unsafe_allow_html=True,
            )


def pipeline_stepper(steps: Iterable[tuple[str, str]]) -> None:
    html = '<div class="prism-pipeline">'
    for label, state in steps:
        html += f'<span class="prism-step {escape(state)}">{escape(label)}</span>'
    st.markdown(html + "</div>", unsafe_allow_html=True)


def panel_title(title: str, caption: str | None = None) -> None:
    st.markdown(f"#### {escape(title)}")
    if caption:
        st.markdown(f'<div class="prism-panel-caption">{escape(caption)}</div>', unsafe_allow_html=True)


def escape_html(value: Any) -> str:
    return escape(str(value))
