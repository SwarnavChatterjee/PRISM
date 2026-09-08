"""Normalize vendor-specific configuration into the canonical baseline model.

The MVP follows a safe cascade: deterministic YAML patterns are implemented
first; semantic and LLM suggestions remain explicit extension points and never
silently turn an unknown line into a trusted control.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from src.normalization.patterns import load_vendor_patterns, match_line
from src.schema.baseline import DeviceConfig, DeviceInfo, SecurityBaseline
from src.training.loop import TrainingLoop


class NormalizationEngine:
    def __init__(self, vendor: str = "unknown", db_path: Optional[str] = None) -> None:
        self.vendor = vendor.lower()
        self.patterns = load_vendor_patterns(self.vendor)
        self.training_loop = TrainingLoop(db_path) if db_path else None

    def normalize_config(self, raw_text: str) -> DeviceConfig:
        values: Dict[str, Any] = {}
        unmapped = []
        provenance: Dict[str, Dict[str, Any]] = {}

        for line_no, raw_line in enumerate(raw_text.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("!") or line.startswith("#"):
                continue
            result = self.tier1_exact_match(line)
            if result is None and self.training_loop is not None:
                result = self.training_loop.apply_learned_mapping(line, self.vendor)
            if result:
                schema_path, value, confidence = result
                if isinstance(value, dict) and value.get("__prism_operation__") == "increment":
                    current = self._get_nested_value(values, schema_path, default=0)
                    value = current + 1
                self._set_nested_value(values, schema_path, value)
                provenance[schema_path] = {
                    "source_line": line_no,
                    "raw": raw_line,
                    "confidence": confidence,
                }
            else:
                unmapped.append({"line_no": line_no, "raw": raw_line, "status": "needs_training"})

        baseline = SecurityBaseline(**values.get("baseline", {}))
        return DeviceConfig(
            device=DeviceInfo(hostname="unknown", vendor=self.vendor, os_version="unknown"),
            baseline=baseline,
            unmapped_lines=unmapped,
            provenance=provenance,
            metadata={
                "normalization_tiers": {
                    "tier1": "enabled",
                    "tier2": "not_configured",
                    "tier3": "human_confirmation_required",
                }
            },
        )

    def tier1_exact_match(self, line: str) -> Optional[Tuple[str, Any, float]]:
        return match_line(line, self.patterns)

    def tier2_fuzzy_match(self, line: str) -> Optional[Tuple[str, float]]:
        """Semantic matching hook; disabled until model loading is configured."""
        return None

    def tier3_llm_suggestion(self, line: str) -> Optional[Tuple[str, float]]:
        """LLM suggestion hook; results require human confirmation."""
        return None

    @staticmethod
    def _set_nested_value(obj: Dict[str, Any], path: str, value: Any) -> None:
        keys = path.split(".")
        current = obj
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value

    @staticmethod
    def _get_nested_value(obj: Dict[str, Any], path: str, default: Any = None) -> Any:
        current: Any = obj
        for key in path.split("."):
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current


def normalize_config(
    raw_text: str, vendor_hint: str = "unknown", db_path: Optional[str] = None
) -> DeviceConfig:
    return NormalizationEngine(vendor_hint, db_path=db_path).normalize_config(raw_text)


def tier1_exact_match(line: str, vendor: str) -> Optional[Tuple[str, Any, float]]:
    return NormalizationEngine(vendor).tier1_exact_match(line)
