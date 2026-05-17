from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .bottleneck import BottleneckPrediction
from .common import ProvenanceInfo
from .inventory import InventoryPrediction
from .maintenance import MaintenancePrediction


AlertLevel = Literal["Routine", "Watch", "Priority", "Critical"]
PriorityLevel = Literal["P1", "P2", "P3", "P4"]


class ActionItem(BaseModel):
    priority: PriorityLevel
    team: str
    description: str
    rationale: str
    expected_impact: str


class ReadinessFactor(BaseModel):
    label: str
    impact: float = Field(..., ge=0)
    detail: str


class FusionInput(BaseModel):
    passenger_load: int = Field(..., ge=0, le=400)
    arrival_delay: int = Field(..., ge=0, le=240)
    gate_congestion: float = Field(..., ge=0, le=10)
    assistance_request: bool = False
    assistance_equipment_confirmed: bool = False
    maintenance: MaintenancePrediction
    inventory: InventoryPrediction
    bottleneck: BottleneckPrediction


class FusionPrediction(BaseModel):
    readiness_score: float = Field(..., ge=0, le=100)
    criticality_score: float = Field(..., ge=0, le=100)
    alert_level: AlertLevel
    at_risk: bool
    alert_summary: list[str]
    readiness_breakdown: list[ReadinessFactor]
    action_queue: list[ActionItem]
    expected_delay_risk_min: float = Field(..., ge=0)
    expected_benefit_min: float = Field(..., ge=0)
    proactive_vs_reactive_delta_min: float = Field(..., ge=0)
    explanation: str
    provenance: ProvenanceInfo
