from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .common import ProvenanceInfo


InventoryRiskLevel = Literal["LOW", "ELEVATED", "HIGH"]


class InventoryInput(BaseModel):
    route_class: str = Field(..., examples=["short_haul"])
    passenger_load: int = Field(..., ge=0, le=400)
    service_profile: str = Field(..., examples=["business_priority"])
    shortage_score: float = Field(..., ge=0, le=10)
    trolley_availability: float = Field(..., ge=0, le=1)
    catering_complexity: float = Field(..., ge=0, le=10)
    turnaround_pressure: float = Field(..., ge=0, le=10)
    item_criticality: float = Field(..., ge=0, le=10)
    inventory_category: str = Field(..., examples=["beverage"])


class InventoryPrediction(BaseModel):
    shortage_risk: float = Field(..., ge=0, le=1)
    risk_level: InventoryRiskLevel
    affected_service_area: str
    confidence: float = Field(..., ge=0, le=1)
    trolley_status: str
    top_factors: list[str]
    recommendation: str
    explanation: str
    model_source: str
    provenance: ProvenanceInfo
