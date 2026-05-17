from __future__ import annotations

from fastapi import APIRouter

from app.schemas.demo import ScenarioInput
from app.schemas.maintenance import MaintenanceInput, MaintenancePrediction
from app.services.maintenance_service import predict_maintenance
from app.services.scenario_service import to_maintenance_input

router = APIRouter(tags=["maintenance"])


@router.post("/predict/maintenance", response_model=MaintenancePrediction)
def maintenance_prediction(payload: MaintenanceInput | ScenarioInput) -> MaintenancePrediction:
    module_input = to_maintenance_input(payload) if isinstance(payload, ScenarioInput) else payload
    return predict_maintenance(module_input)
