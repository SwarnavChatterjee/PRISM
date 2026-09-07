"""HTTP API exposing the existing PRISM Python engine to the React client."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.compliance.engine import evaluate_device
from src.ingestion.uploader import decode_config, detect_vendor
from src.normalization.engine import normalize_config
from src.training.loop import TrainingLoop


class AnalysisResponse(BaseModel):
    filename: str
    vendor: str
    detection_confidence: float
    raw_config: str
    device_config: dict[str, Any]
    compliance: dict[str, Any]


class TrainingRequest(BaseModel):
    filename: str = "active-configuration"
    raw_config: str
    vendor: str
    raw_line: str
    schema_path: str
    mapped_value: Any = True
    created_by: str = "admin"


app = FastAPI(title="PRISM API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _model_dump(model: Any) -> dict[str, Any]:
    return model.model_dump() if hasattr(model, "model_dump") else model.dict()


def _analysis(filename: str, raw_config: str, vendor: str | None = None) -> AnalysisResponse:
    detected, confidence = detect_vendor(raw_config)
    selected_vendor = (vendor or detected or "unknown").lower()
    config = normalize_config(raw_config, selected_vendor)
    config_data = _model_dump(config)
    return AnalysisResponse(
        filename=filename,
        vendor=selected_vendor,
        detection_confidence=confidence,
        raw_config=raw_config,
        device_config=config_data,
        compliance=evaluate_device(config_data, "cis_benchmarks"),
    )


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "prism-api"}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze(file: UploadFile = File(...), vendor: str = Form("")) -> AnalysisResponse:
    try:
        content = await file.read()
        raw_config = decode_config(file.filename or "configuration.txt", content)
        return _analysis(file.filename or "configuration.txt", raw_config, vendor or None)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/train", response_model=AnalysisResponse)
def train(request: TrainingRequest) -> AnalysisResponse:
    if not request.schema_path.startswith("baseline."):
        raise HTTPException(status_code=400, detail="Mappings must target the canonical baseline schema")
    loop = TrainingLoop()
    loop.save_mapping(
        request.vendor,
        request.raw_line,
        request.schema_path,
        created_by=request.created_by,
        mapped_value=request.mapped_value,
    )
    config = normalize_config(request.raw_config, request.vendor, db_path="compliance.db")
    data = _model_dump(config)
    return AnalysisResponse(
        filename=request.filename,
        vendor=request.vendor,
        detection_confidence=1.0,
        raw_config=request.raw_config,
        device_config=data,
        compliance=evaluate_device(data, "cis_benchmarks"),
    )
