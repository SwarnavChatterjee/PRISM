"""
Normalization Engine — Core AI/NLP Component
Converts vendor-specific config syntax into canonical Security Baseline Model
"""

from typing import Optional, Tuple, Dict, Any
from src.schema.baseline import DeviceConfig

def normalize_config(raw_text: str, vendor_hint: str = None) -> DeviceConfig:
    """
    Main entry point for normalization.
    
    TODO: Implement with three-tier cascade:
    1. Exact pattern matching (regex)
    2. Fuzzy matching (embeddings)
    3. LLM suggestion + human confirmation
    """
    pass

def tier1_exact_match(line: str, vendor: str) -> Optional[Tuple[str, Any, float]]:
    """Try exact pattern match. Returns (schema_path, value, confidence) or None."""
    pass

def tier2_fuzzy_match(line: str) -> Optional[Tuple[str, float]]:
    """Try embedding similarity. Returns (schema_path, confidence) or None."""
    pass

def tier3_llm_suggestion(line: str) -> Optional[Tuple[str, float]]:
    """LLM-based suggestion (human-confirmed only). Returns (schema_path, confidence)."""
    pass
