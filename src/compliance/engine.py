"""Data-driven compliance evaluation for normalized device configurations."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class Finding:
    control_id: str
    control_name: str
    status: str
    severity: str
    source_line: int
    raw_config_line: str
    remediation_command: str
    rationale: str = ""
    references: List[Dict[str, Any]] = field(default_factory=list)


def load_framework(framework_name: str) -> List[Dict[str, Any]]:
    path = Path(__file__).resolve().parents[2] / "data" / "frameworks" / f"{framework_name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Framework rules not found: {framework_name}")
    with path.open(encoding="utf-8") as handle:
        rules = yaml.safe_load(handle) or []
    if not isinstance(rules, list):
        raise ValueError(f"Framework must contain a list of rules: {path}")
    return rules


def _get_nested_value(obj: Dict[str, Any], path: str) -> Any:
    current: Any = obj
    for key in path.split("."):
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def evaluate_rule(config_value: Any, rule: Dict[str, Any]) -> bool:
    operator = rule.get("operator", "==")
    expected = rule.get("expected_value", rule.get("expected"))
    if config_value is None:
        return False
    if operator == "==":
        return config_value == expected
    if operator == "!=":
        return config_value != expected
    if operator == ">":
        return config_value > expected
    if operator == "<":
        return config_value < expected
    if operator == ">=":
        return config_value >= expected
    if operator == "<=":
        return config_value <= expected
    if operator == "in":
        return config_value in expected
    if operator == "contains":
        return expected in str(config_value)
    raise ValueError(f"Unsupported compliance operator: {operator}")


class ComplianceEngine:
    def __init__(self, framework: str = "cis_benchmarks") -> None:
        self.framework = framework
        self.rules = self._load_live_rules(framework)

    @staticmethod
    def _load_live_rules(framework: str) -> List[Dict[str, Any]]:
        """Load only controls supported by the current baseline schema.

        Research-stage controls remain in the framework file for provenance,
        but are marked as proposed_schema_extension until their fields are
        added to the canonical model.
        """
        return [
            rule
            for rule in load_framework(framework)
            if rule.get("status") != "proposed_schema_extension"
        ]

    def evaluate_device(self, device_config: Dict[str, Any], framework: Optional[str] = None) -> Dict[str, Any]:
        if framework and framework != self.framework:
            self.framework = framework
            self.rules = self._load_live_rules(framework)
        findings = [self._evaluate_rule(device_config, rule) for rule in self.rules]
        failed = [finding for finding in findings if finding.status == "fail"]
        return {
            "device_id": device_config.get("device", {}).get("hostname", "unknown"),
            "framework": self.framework,
            "total_controls": len(findings),
            "passed": len(findings) - len(failed),
            "failed": len(failed),
            "critical_count": sum(1 for f in failed if f.severity == "critical"),
            "findings": [asdict(finding) for finding in findings],
        }

    def _evaluate_rule(self, device_config: Dict[str, Any], rule: Dict[str, Any]) -> Finding:
        schema_path = rule["schema_path"]
        actual = _get_nested_value(device_config, schema_path)
        passed = evaluate_rule(actual, rule)
        source = device_config.get("provenance", {}).get(schema_path, {})
        if not source:
            source = device_config.get("provenance", {}).get(schema_path.split(".")[-1], {})
        return Finding(
            control_id=rule["id"],
            control_name=rule.get("name", rule.get("control", rule["id"])),
            status="pass" if passed else "fail",
            severity=rule.get("severity", "medium"),
            source_line=source.get("source_line", -1),
            raw_config_line=source.get("raw", "N/A"),
            remediation_command=rule.get("remediation_template", rule.get("remediation", "N/A")),
            rationale=rule.get("rationale", ""),
            references=rule.get("references", []) or [],
        )


def evaluate_device(device_config: Dict[str, Any], framework: str = "cis_benchmarks") -> Dict[str, Any]:
    return ComplianceEngine(framework).evaluate_device(device_config)
