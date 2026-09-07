"""File-upload helpers used by the Streamlit MVP."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple


SUPPORTED_EXTENSIONS = {".cfg", ".conf", ".config", ".txt", ".set"}


def decode_config(filename: str, content: bytes) -> str:
    """Decode an uploaded configuration after validating its file type."""
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported configuration type: {suffix or 'none'}")
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Configuration must be a UTF-8 text file") from exc


def detect_vendor(raw_text: str) -> Tuple[str, float]:
    """Return a conservative vendor guess and confidence."""
    lines = [line.strip().lower() for line in raw_text.splitlines() if line.strip()]
    joined = "\n".join(lines)
    if any(line.startswith("set ") for line in lines) or "junos" in joined:
        return "juniper", 0.85
    if "cisco ios" in joined or any("interface gigabitethernet" in line for line in lines):
        return "cisco", 0.85
    if any(token in joined for token in ("ip ssh version", "aaa new-model", "no ip http server")):
        return "cisco", 0.65
    return "unknown", 0.0
