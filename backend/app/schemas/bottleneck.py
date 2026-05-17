from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .common import ProvenanceInfo


BottleneckLabel = Literal["Maintenance", "Catering", "Cleaning", "Boarding", "Refueling"]


class BottleneckInput(BaseModel):
    passenger_load: int = Field(..., ge=0, le=400)
    arrival_delay: int = Field(..., ge=0, le=240)
    gate_congestion: float = Field(..., ge=0, le=10)
    malfunction_count: int = Field(..., ge=0)
    malfunction_severity: float = Field(..., ge=0, le=10)
    inventory_shortage: float = Field(..., ge=0, le=10)
    aircraft_type: str = Field(..., examples=["A320neo"])
    route_class: str = Field(..., examples=["short_haul"])
    assistance_request: bool = False
    refueling_required: bool = True
    weather_disturbance: float = Field(default=0, ge=0, le=10)


class BottleneckDistribution(BaseModel):
    Maintenance: float = Field(..., ge=0, le=1)
    Catering: float = Field(..., ge=0, le=1)
    Cleaning: float = Field(..., ge=0, le=1)
    Boarding: float = Field(..., ge=0, le=1)
    Refueling: float = Field(..., ge=0, le=1)


class BottleneckPrediction(BaseModel):
    probabilities: BottleneckDistribution
    dominant_bottleneck: BottleneckLabel
    confidence: float = Field(..., ge=0, le=1)
    top_contributing_factors: list[str]
    explanation: str
    recommended_response: str
    model_source: str
    provenance: ProvenanceInfo
