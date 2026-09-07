"""Finding table helpers shared by the dashboard and results page."""

from __future__ import annotations

from typing import Any

import streamlit as st

from frontend.ui import TONE_FG, escape_html


def detect_columns(columns: list[str]) -> dict[str, str | None]:
    normalized = {column.lower(): column for column in columns}
    return {
        "status": normalized.get("status"),
        "severity": normalized.get("severity"),
        "control": normalized.get("control_id") or normalized.get("control"),
    }


def style_findings(dataframe):
    if dataframe.empty:
        return dataframe

    def color_status(value):
        tone = "pass" if str(value).lower() == "pass" else "critical"
        return f"color: {TONE_FG[tone]}; font-weight: 700"

    def color_severity(value):
        tone = "critical" if str(value).lower() in {"critical", "high"} else "medium"
        return f"color: {TONE_FG[tone]}; font-weight: 650"

    styles = dataframe.style
    if "status" in dataframe.columns:
        styles = styles.map(color_status, subset=["status"])
    if "severity" in dataframe.columns:
        styles = styles.map(color_severity, subset=["severity"])
    return styles


def priority_findings(findings: list[dict[str, Any]], limit: int = 6):
    columns = detect_columns(list(findings[0].keys()) if findings else [])
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    records = sorted(
        findings,
        key=lambda item: (
            0 if str(item.get("status", "")).lower() == "fail" else 1,
            severity_order.get(str(item.get("severity", "medium")).lower(), 4),
        ),
    )[:limit]
    return records, columns


def render_finding_row(record: dict[str, Any], columns: dict[str, str | None]) -> None:
    status = str(record.get(columns["status"] or "status", "")).upper()
    severity = str(record.get(columns["severity"] or "severity", "")).title()
    control = record.get(columns["control"] or "control_id", "Control")
    name = record.get("control_name", record.get("name", ""))
    tone = "pass" if status == "PASS" else "critical" if severity.lower() in {"critical", "high"} else "medium"
    st.markdown(
        f'<div class="prism-kv"><b>{escape_html(control)}</b> · {escape_html(name)} '
        f'<span style="color:{TONE_FG[tone]};font-weight:700">{escape_html(status)}</span> '
        f'<span style="color:{TONE_FG[tone]}">{escape_html(severity)}</span></div>',
        unsafe_allow_html=True,
    )
