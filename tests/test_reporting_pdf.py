from io import BytesIO

from pypdf import PdfReader
from fastapi.testclient import TestClient

from api.main import app

from src.reporting.pdf import generate_compliance_pdf


def test_generate_compliance_pdf_contains_report_sections():
    analysis = {
        "filename": "cisco_demo.txt",
        "vendor": "cisco",
        "detection_confidence": 0.85,
        "device_config": {
            "device": {"hostname": "edge-01", "os_version": "ios", "vendor": "cisco"},
            "unmapped_lines": [{"line_no": 12, "raw": "banner login ^C", "status": "unmapped"}],
        },
        "compliance": {
            "framework": "cis_benchmarks",
            "total_controls": 2,
            "passed": 1,
            "failed": 1,
            "critical_count": 0,
            "findings": [
                {
                    "control_id": "CIS-1.1",
                    "control_name": "SSH version 2 enforced",
                    "status": "fail",
                    "severity": "high",
                    "source_line": 4,
                    "raw_config_line": "ip ssh version 1",
                    "remediation_command": "ip ssh version 2",
                    "rationale": "Legacy SSH exposes weaker cryptography.",
                    "references": [{"source": "CIS Cisco IOS Benchmark"}],
                }
            ],
        },
    }

    pdf = generate_compliance_pdf(analysis)
    assert pdf.startswith(b"%PDF")
    reader = PdfReader(BytesIO(pdf))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert "PRISM Compliance Report" in text
    assert "SSH version 2 enforced" in text
    assert "Why it matters" in text
    assert "CIS Cisco IOS Benchmark" in text
    assert "Unmapped configuration lines" in text


def test_pdf_endpoint_returns_downloadable_pdf():
    analysis = {
        "filename": "edge.txt",
        "vendor": "cisco",
        "detection_confidence": 1.0,
        "raw_config": "ip ssh version 2",
        "device_config": {"device": {"hostname": "edge-01"}, "unmapped_lines": []},
        "compliance": {
            "framework": "cis_benchmarks",
            "total_controls": 1,
            "passed": 1,
            "failed": 0,
            "critical_count": 0,
            "findings": [],
        },
    }
    response = TestClient(app).post("/api/report/pdf", json=analysis)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "edge-compliance-report.pdf" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")
