from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .common import ProvenanceInfo


UrgencyClass = Literal["OK", "PLAN", "SOON", "CRITICAL"]


class MaintenanceInput(BaseModel):
    aircraft_type: str = Field(..., examples=["A320neo"])
    component_type: str = Field(..., examples=["galley_chiller"])
    aircraft_age_cycles: int = Field(..., ge=0)
    flight_duration_hr: float = Field(..., ge=0.5)
    cabin_temperature: float = Field(..., ge=10, le=45)
    humidity: float = Field(..., ge=5, le=100)
    passenger_load: int = Field(..., ge=0, le=400)
    cycles_since_install: int = Field(..., ge=0)
    wear_index: float = Field(..., ge=0, le=100)
    malfunction_count: int = Field(..., ge=0)
    malfunction_severity: float = Field(..., ge=0, le=10)
    environmental_stress: float = Field(..., ge=0, le=10)


class MaintenancePrediction(BaseModel):
    failure_probability: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    remaining_flights_estimate: int = Field(..., ge=0)
    urgency_class: UrgencyClass
    anomaly_flag: bool
    affected_components: list[str]
    top_factors: list[str]
    explanation: str
    recommended_action: str
    model_source: str
    provenance: ProvenanceInfo
