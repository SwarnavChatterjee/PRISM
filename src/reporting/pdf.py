"""Deterministic PDF reports for PRISM compliance analyses."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


PAGE_WIDTH, PAGE_HEIGHT = A4
NAVY = colors.HexColor("#18212f")
BLUE = colors.HexColor("#2554c7")
BLUE_SOFT = colors.HexColor("#eaf0fd")
INK = colors.HexColor("#1d2733")
MUTED = colors.HexColor("#627083")
FAINT = colors.HexColor("#98a2b3")
LINE = colors.HexColor("#dbe2ea")
LINE_SOFT = colors.HexColor("#eef1f5")
PANEL = colors.HexColor("#f4f7fb")
WHITE = colors.white
GREEN = colors.HexColor("#177245")
RED = colors.HexColor("#b42318")
AMBER = colors.HexColor("#a15c00")
GRAY_SOFT = colors.HexColor("#eef1f5")

SEVERITY_COLORS = {
    "CRITICAL": (RED, colors.HexColor("#fbeaea")),
    "HIGH": (RED, colors.HexColor("#fbeaea")),
    "MEDIUM": (AMBER, colors.HexColor("#fbf0dd")),
    "LOW": (MUTED, GRAY_SOFT),
}


def _safe(value: Any, fallback: str = "N/A") -> str:
    """Return readable ASCII-safe text for PDF content."""
    if value is None or value == "":
        return fallback
    text = str(value)
    replacements = {
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def _escape(value: Any, fallback: str = "N/A") -> str:
    from xml.sax.saxutils import escape

    return escape(_safe(value, fallback)).replace("\n", "<br/>")


def _paragraph(text: Any, style: ParagraphStyle, fallback: str = "N/A") -> Paragraph:
    return Paragraph(_escape(text, fallback), style)


def _title_case(value: Any, fallback: str = "N/A") -> str:
    text = _safe(value, fallback)
    return text if text == fallback else text.replace("_", " ").strip().title()


class HRule(Flowable):
    def __init__(self, width, color=LINE_SOFT, thickness=0.75):
        super().__init__()
        self.width = width
        self.color = color
        self.thickness = thickness
        self.height = thickness

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)


class SectionHeading(Flowable):
    def __init__(self, text, styles, accent=BLUE):
        super().__init__()
        self.para = _paragraph(text, styles["section"])
        self.accent = accent
        self.height = 0

    def wrap(self, availWidth, availHeight):
        _, height = self.para.wrap(availWidth, availHeight)
        self.width = availWidth
        self.height = height + 6
        return self.width, self.height

    def draw(self):
        self.para.drawOn(self.canv, 0, self.height - self.para.height + 2)
        self.canv.setStrokeColor(self.accent)
        self.canv.setLineWidth(1.6)
        self.canv.line(0, 0, 16 * mm, 0)


class ProportionBar(Flowable):
    def __init__(self, width, passed, failed, other, height=6 * mm):
        super().__init__()
        self.width = width
        self.height = height
        total = max(passed + failed + other, 1)
        self.segments = [(passed / total, GREEN), (failed / total, RED), (other / total, FAINT)]

    def draw(self):
        canvas = self.canv
        x = 0
        radius = self.height / 2
        canvas.saveState()
        path = canvas.beginPath()
        path.roundRect(0, 0, self.width, self.height, radius)
        canvas.clipPath(path, stroke=0)
        for fraction, color in self.segments:
            if fraction <= 0:
                continue
            segment_width = fraction * self.width
            canvas.setFillColor(color)
            canvas.rect(x, 0, segment_width + 0.5, self.height, stroke=0, fill=1)
            x += segment_width
        canvas.restoreState()
        canvas.setStrokeColor(LINE)
        canvas.roundRect(0, 0, self.width, self.height, radius, stroke=1, fill=0)


class NumberedCanvas(Canvas):
    """Canvas that adds a stable 'Page X of Y' footer after pagination."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict] = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_footer(total_pages)
            super().showPage()
        super().save()

    def _draw_footer(self, total_pages):
        self.setStrokeColor(LINE)
        self.setLineWidth(0.75)
        self.line(16 * mm, 9 * mm, PAGE_WIDTH - 16 * mm, 9 * mm)
        self.setFont("Helvetica", 7)
        self.setFillColor(FAINT)
        self.drawString(16 * mm, 5.6 * mm, "Generated by the deterministic PRISM compliance engine")
        self.drawRightString(PAGE_WIDTH - 16 * mm, 5.6 * mm, f"Page {self._pageNumber} of {total_pages}")


class _ReportDocTemplate(BaseDocTemplate):
    def __init__(self, buffer: BytesIO, filename: str):
        super().__init__(
            buffer,
            pagesize=A4,
            leftMargin=16 * mm,
            rightMargin=16 * mm,
            topMargin=20 * mm,
            bottomMargin=14 * mm,
            title=f"PRISM Compliance Report - {filename}",
            author="PRISM",
        )
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="content")
        self.addPageTemplates([PageTemplate(id="report", frames=frame, onPage=self._draw_page)])

    def _draw_page(self, canvas, doc) -> None:
        canvas.saveState()
        mark_x, mark_y, mark_size = self.leftMargin, PAGE_HEIGHT - 12.6 * mm, 4 * mm
        canvas.setFillColor(NAVY)
        canvas.roundRect(mark_x, mark_y, mark_size, mark_size, 1, stroke=0, fill=1)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 7)
        canvas.drawCentredString(mark_x + mark_size / 2, mark_y + 1.2, "P")
        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(NAVY)
        canvas.drawString(mark_x + mark_size + 2.2 * mm, PAGE_HEIGHT - 11.8 * mm, "PRISM")
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(PAGE_WIDTH - self.rightMargin, PAGE_HEIGHT - 11.6 * mm, "Compliance Report")
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.75)
        canvas.line(self.leftMargin, PAGE_HEIGHT - 15 * mm, PAGE_WIDTH - self.rightMargin, PAGE_HEIGHT - 15 * mm)
        canvas.restoreState()


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("ReportTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=18, leading=21, textColor=NAVY, alignment=TA_LEFT, spaceAfter=2),
        "subtitle": ParagraphStyle("ReportSubtitle", parent=base["Normal"], fontName="Helvetica", fontSize=9, leading=12, textColor=MUTED, spaceAfter=1),
        "eyebrow": ParagraphStyle("Eyebrow", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=7.5, leading=9, textColor=BLUE, spaceAfter=3),
        "section": ParagraphStyle("Section", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=13, textColor=NAVY),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontName="Helvetica", fontSize=8.5, leading=12, textColor=INK),
        "small": ParagraphStyle("Small", parent=base["BodyText"], fontName="Helvetica", fontSize=7.3, leading=9.5, textColor=MUTED),
        "small_dark": ParagraphStyle("SmallDark", parent=base["BodyText"], fontName="Helvetica", fontSize=7.8, leading=9.5, textColor=INK),
        "metric": ParagraphStyle("Metric", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=16, leading=18, textColor=NAVY, alignment=TA_CENTER),
        "metric_label": ParagraphStyle("MetricLabel", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=6.2, leading=8, textColor=MUTED, alignment=TA_CENTER),
        "table_head": ParagraphStyle("TableHead", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=7.5, leading=9, textColor=colors.white),
        "table": ParagraphStyle("Table", parent=base["BodyText"], fontName="Helvetica", fontSize=7.8, leading=10.5, textColor=INK),
        "table_bold": ParagraphStyle("TableBold", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=7.8, leading=10.5, textColor=INK),
        "label": ParagraphStyle("Label", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=7, leading=9, textColor=MUTED),
        "code": ParagraphStyle("Code", parent=base["Code"], fontName="Courier", fontSize=7.6, leading=11, textColor=INK, backColor=PANEL, borderColor=LINE, borderWidth=0.5, borderPadding=5),
        "center": ParagraphStyle("Center", parent=base["BodyText"], fontName="Helvetica", fontSize=8, leading=10, textColor=MUTED, alignment=TA_CENTER),
        "right": ParagraphStyle("Right", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=INK, alignment=TA_RIGHT),
        "finding_title": ParagraphStyle("FindingTitle", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=8.6, leading=11.5, textColor=NAVY),
    }


def _metric_table(analysis: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    compliance = analysis.get("compliance") or {}
    total = int(compliance.get("total_controls") or 0)
    passed = int(compliance.get("passed") or 0)
    failed = int(compliance.get("failed") or 0)
    critical = int(compliance.get("critical_count") or 0)
    score_pct = round((passed / total) * 100) if total else 0
    score = f"{score_pct}%"
    score_color = GREEN if score_pct >= 80 else AMBER if score_pct >= 50 else RED
    values = [(score, "COMPLIANCE SCORE", score_color), (str(total), "CONTROLS CHECKED", NAVY), (str(passed), "PASSED", GREEN), (str(failed), "FAILED", RED if failed else NAVY), (str(critical), "CRITICAL", AMBER if critical else NAVY)]
    value_styles = [ParagraphStyle(f"MetricV{i}", parent=styles["metric"], textColor=color, alignment=TA_LEFT) for i, (_, _, color) in enumerate(values)]
    label_style = ParagraphStyle("MetricLabelLeft", parent=styles["metric_label"], alignment=TA_LEFT)
    content_width = 178 * mm
    col_width = content_width / 5
    data = [[_paragraph(value, value_styles[i]) for i, (value, _, _) in enumerate(values)], [_paragraph(label, label_style) for _, label, _ in values]]
    table = Table(data, colWidths=[col_width] * 5)
    table.setStyle(TableStyle([
        ("LINEAFTER", (0, 0), (3, -1), 0.5, LINE),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
        ("LEFTPADDING", (1, 0), (-1, -1), 5 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),
        ("TOPPADDING", (0, 1), (-1, 1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
    ]))
    legend = Table([[
        _paragraph("Passed", ParagraphStyle("LegP", parent=styles["small"], textColor=GREEN)),
        _paragraph("Failed", ParagraphStyle("LegF", parent=styles["small"], textColor=RED)),
        _paragraph("Not evaluated", ParagraphStyle("LegO", parent=styles["small"], textColor=FAINT)),
    ]], colWidths=[content_width / 3] * 3)
    legend.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    wrapper = Table([[table], [HRule(content_width, color=LINE)], [Spacer(1, 3.5 * mm)], [ProportionBar(content_width, passed, failed, max(total - passed - failed, 0))], [Spacer(1, 1.2 * mm)], [legend]], colWidths=[content_width])
    wrapper.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return wrapper


def _metadata_table(analysis: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    device = analysis.get("device_config") or {}
    device_info = device.get("device") or {}
    rows = [
        ("Configuration file", analysis.get("filename")),
        ("Vendor", _title_case(analysis.get("vendor"))),
        ("Detection confidence", f"{round(float(analysis.get('detection_confidence') or 0) * 100)}%"),
        ("Hostname", device_info.get("hostname")),
        ("OS version", device_info.get("os_version")),
        ("Framework", _title_case((analysis.get("compliance") or {}).get("framework", "cis_benchmarks"))),
    ]
    data = [[_paragraph(label, styles["table_bold"]), _paragraph(value, styles["table"])] for label, value in rows]
    table = Table(data, colWidths=[42 * mm, 128 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, LINE_SOFT),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def _status_color(status: str):
    return GREEN if status == "pass" else RED if status == "fail" else AMBER


def _finding_blocks(findings: Iterable[dict[str, Any]], styles: dict[str, ParagraphStyle]) -> list[Any]:
    blocks: list[Any] = []
    for finding in findings:
        status = _safe(finding.get("status"), "info").upper()
        severity = _safe(finding.get("severity"), "medium").upper()
        source_value = finding.get("source_line")
        source_line = "N/A" if source_value in (None, "", -1, "-1") else source_value
        sev_color, _ = SEVERITY_COLORS.get(severity, (MUTED, GRAY_SOFT))
        status_color = GREEN if status == "PASS" else RED if status == "FAIL" else MUTED
        content_width = 178 * mm
        header = Table([[
            Paragraph(
                f'<font color="#{MUTED.hexval()[2:]}">{_escape(finding.get("control_id"))} &#183; line {_escape(source_line)}</font><br/>'
                f'<font size="8.6"><b>{_escape(finding.get("control_name"), "N/A")}</b></font>',
                styles["finding_title"],
            ),
            Paragraph(
                f'<font color="#{sev_color.hexval()[2:]}">{_escape(severity)}</font>'
                f'<font color="#{MUTED.hexval()[2:]}"> &#183; </font>'
                f'<font color="#{status_color.hexval()[2:]}">{_escape(status)}</font>',
                ParagraphStyle("StatusLine", parent=styles["small"], fontName="Helvetica-Bold", fontSize=7.2, alignment=TA_RIGHT),
            ),
        ]], colWidths=[content_width - 32 * mm, 32 * mm])
        header.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        detail = Table([
            [_paragraph("Observed", styles["label"]), _paragraph(finding.get("raw_config_line"), styles["code"], "N/A")],
            [_paragraph("Remediation", styles["label"]), _paragraph(finding.get("remediation_command"), styles["code"], "N/A")],
        ], colWidths=[24 * mm, content_width - 24 * mm])
        detail.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 1.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ]))
        finding_story: list[Any] = [header, Spacer(1, 1.5), detail]
        rationale = finding.get("rationale")
        if rationale:
            finding_story.extend([Spacer(1, 1.5 * mm), _paragraph(f"Why it matters: {_safe(rationale)}", styles["small_dark"])])
        references = finding.get("references") or []
        if references:
            sources = "; ".join(_safe(ref.get("source", ref) if isinstance(ref, dict) else ref) for ref in references)
            finding_story.extend([Spacer(1, 1.5 * mm), _paragraph(f"Reference: {sources}", styles["small"])])
        finding_story.extend([Spacer(1, 1.5 * mm), HRule(content_width, color=LINE_SOFT), Spacer(1, 2 * mm)])
        blocks.append(KeepTogether(finding_story))
    return blocks


def generate_compliance_pdf(analysis: dict[str, Any]) -> bytes:
    """Render an analysis response into a polished, deterministic PDF."""
    if not isinstance(analysis, dict):
        raise TypeError("analysis must be a dictionary")
    styles = _styles()
    buffer = BytesIO()
    filename = _safe(analysis.get("filename"), "configuration")
    doc = _ReportDocTemplate(buffer, filename)
    compliance = analysis.get("compliance") or {}
    device = analysis.get("device_config") or {}
    findings = compliance.get("findings") or []
    unmapped = device.get("unmapped_lines") or []
    content_width = doc.width
    generated = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %b %Y, %H:%M IST")
    story: list[Any] = [
        _paragraph("COMPLIANCE ASSESSMENT", styles["eyebrow"]),
        _paragraph("PRISM Compliance Report", styles["title"]),
        _paragraph(f"{_safe(analysis.get('filename'), 'configuration')} - generated {generated}", styles["subtitle"]),
        Spacer(1, 3 * mm),
        _metric_table(analysis, styles),
        Spacer(1, 3.5 * mm),
        SectionHeading("Assessment context", styles),
        Spacer(1, 2 * mm),
        _metadata_table(analysis, styles),
        Spacer(1, 3.5 * mm),
        SectionHeading(f"Control findings ({len(findings)})", styles),
        Spacer(1, 2.5 * mm),
    ]
    if findings:
        story.extend(_finding_blocks(findings, styles))
    else:
        story.append(_paragraph("No controls were evaluated.", styles["body"]))
    if unmapped:
        story.extend([
            Spacer(1, 4 * mm),
            SectionHeading("Unmapped configuration lines", styles),
            Spacer(1, 2 * mm),
            _paragraph("These lines were not mapped to the canonical baseline and were excluded from compliance scoring.", styles["body"]),
            Spacer(1, 2.5 * mm),
        ])
        rows = [[_paragraph("LINE", styles["table_head"]), _paragraph("STATUS", styles["table_head"]), _paragraph("RAW CONFIGURATION", styles["table_head"])] ]
        for item in unmapped:
            rows.append([_paragraph(item.get("line_no"), styles["table"]), _paragraph(item.get("status"), styles["table"]), _paragraph(item.get("raw"), styles["code"])])
        table = Table(rows, colWidths=[20 * mm, 28 * mm, content_width - 48 * mm], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("BOX", (0, 0), (-1, -1), 0.75, LINE),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE_SOFT),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PANEL]),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(table)
    story.extend([
        Spacer(1, 2.5 * mm),
        HRule(content_width, color=LINE_SOFT),
        Spacer(1, 1.5 * mm),
        _paragraph("Findings are based on exact YAML-backed rules and source-line provenance. This report was generated automatically and did not require human review.", styles["small"]),
    ])
    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
