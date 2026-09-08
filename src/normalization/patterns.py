"""Vendor pattern loading and deterministic line matching."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

PatternMatch = Tuple[str, Any, float]


def load_vendor_patterns(vendor: str, data_dir: Optional[Path] = None) -> Dict[str, List[dict]]:
    """Load a vendor's YAML pattern library; missing vendors safely return no patterns."""
    root = data_dir or Path(__file__).resolve().parents[2] / "data" / "vendor_patterns"
    path = root / f"{vendor.lower()}_patterns.yaml"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def match_line(line: str, patterns: Dict[str, List[dict]]) -> Optional[PatternMatch]:
    """Return ``(schema_path, value, confidence)`` for the first exact match."""
    for pattern_list in patterns.values():
        for pattern in pattern_list or []:
            expression = pattern.get("regex")
            if not expression:
                continue
            try:
                match = re.search(expression, line, re.IGNORECASE)
            except re.error:
                continue
            if not match:
                continue
            value = pattern.get("value", True)
            value_type = pattern.get("value_type", "str")
            if value_type == "increment":
                value = {"__prism_operation__": "increment"}
            elif match.groups() and "value" not in pattern:
                value = _convert_type(match.group(1), value_type)
            return pattern["schema_path"], value, 1.0
    return None


def _convert_type(value: str, value_type: str) -> Any:
    if value_type == "int":
        return int(value)
    if value_type == "bool":
        return value.lower() in {"true", "yes", "1", "enabled", "on"}
    return value
