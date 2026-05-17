from __future__ import annotations

from pydantic import BaseModel, Field

from .bottleneck import BottleneckPrediction
from .fusion import FusionPrediction
from .inventory import InventoryPrediction
from .maintenance import MaintenancePrediction


class ScenarioInput(BaseModel):
    id: str
    flight_number: str
    aircraft_type: str
    route: str
    route_class: str
    eta: str
    gate: str
    passenger_load: int = Field(..., ge=0, le=400)
    arrival_delay: int = Field(..., ge=0, le=240)
    gate_congestion: float = Field(..., ge=0, le=10)
    assistance_request: bool = False
    assistance_equipment_confirmed: bool = False
    assistance_localization_status: str = "Pending gate coordination"
    inventory_shortage_score: float = Field(..., ge=0, le=10)
    trolley_availability: float = Field(..., ge=0, le=1)
    service_profile: str = "standard"
    catering_complexity: float = Field(default=4, ge=0, le=10)
    turnaround_pressure: float = Field(default=4, ge=0, le=10)
    item_criticality: float = Field(default=5, ge=0, le=10)
    inventory_category: str = "mixed_service"
    malfunction_count: int = Field(..., ge=0)
    malfunction_severity: float = Field(..., ge=0, le=10)
    component_type: str = "seat_power_unit"
    aircraft_age_cycles: int = Field(..., ge=0)
    flight_duration_hr: float = Field(..., ge=0.5)
    cabin_temperature: float = Field(default=23, ge=10, le=45)
    humidity: float = Field(default=35, ge=5, le=100)
    cycles_since_install: int = Field(..., ge=0)
    wear_index: float = Field(..., ge=0, le=100)
    environmental_stress: float = Field(default=3, ge=0, le=10)
    weather_disturbance: float = Field(default=0, ge=0, le=10)
    refueling_required: bool = True
    cabin_report_notes: list[str] = Field(default_factory=list)
    reported_components: list[str] = Field(default_factory=list)


class FlightSummary(BaseModel):
    id: str
    flight_number: str
    aircraft_type: str
    route: str
    eta: str
    gate: str
    arrival_delay: int
    readiness_score: float
    dominant_bottleneck: str
    maintenance_urgency: str
    inventory_alert_status: str
    passenger_assistance_status: str
    alert_level: str
    at_risk: bool


class FlightDetail(BaseModel):
    scenario: ScenarioInput
    maintenance: MaintenancePrediction
    inventory: InventoryPrediction
    bottleneck: BottleneckPrediction
    fusion: FusionPrediction


class DemoFlightsResponse(BaseModel):
    flights: list[FlightSummary]


class DemoScenariosResponse(BaseModel):
    scenarios: list[ScenarioInput]


class RecomputeResponse(BaseModel):
    scenario: ScenarioInput
    maintenance: MaintenancePrediction
    inventory: InventoryPrediction
    bottleneck: BottleneckPrediction
    fusion: FusionPrediction
