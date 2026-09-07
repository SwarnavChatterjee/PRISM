"""Human-confirmed vendor mapping persistence and lookup."""

from __future__ import annotations

import json
import re
from typing import Any, Optional, Tuple

from src.schema.baseline import DeviceConfig
from src.storage.db import connect


class TrainingLoop:
    def __init__(self, db_path: str = "compliance.db") -> None:
        self.db_path = db_path

    def save_mapping(
        self,
        vendor: str,
        raw_line: str,
        schema_path: str,
        created_by: str = "admin",
        confidence: float = 1.0,
        mapped_value: Any = True,
    ) -> bool:
        """Persist a mapping only after an explicit human confirmation."""
        pattern = self._generalize_to_pattern(raw_line)
        with connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO vendor_patterns
                    (vendor, raw_pattern, schema_path, mapped_value, confidence, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (vendor.lower(), pattern, schema_path, json.dumps(mapped_value), confidence, created_by),
            )
            connection.execute(
                "INSERT INTO audit_log (event, user) VALUES (?, ?)",
                (f"mapping_confirmed:{vendor}:{schema_path}", created_by),
            )
        return True

    @staticmethod
    def get_unmapped_lines(device_config: DeviceConfig) -> list[dict]:
        return device_config.unmapped_lines

    @staticmethod
    def _generalize_to_pattern(line: str) -> str:
        escaped = re.escape(line.strip())
        return re.sub(r"\\d+", r"(\\d+)", escaped)

    def apply_learned_mapping(self, line: str, vendor: str) -> Optional[Tuple[str, Any, float]]:
        """Return a human-confirmed mapping matching ``line``, if one exists."""
        with connect(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT raw_pattern, schema_path, mapped_value, confidence
                FROM vendor_patterns WHERE vendor = ? ORDER BY created_at DESC, id DESC
                """,
                (vendor.lower(),),
            ).fetchall()

        for pattern, schema_path, mapped_value, confidence in rows:
            try:
                if re.fullmatch(pattern, line.strip(), re.IGNORECASE):
                    value = json.loads(mapped_value) if mapped_value is not None else True
                    return schema_path, value, confidence
            except (re.error, json.JSONDecodeError):
                continue
        return None
