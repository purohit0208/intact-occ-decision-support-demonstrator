from __future__ import annotations

from fastapi import APIRouter

from app.schemas.demo import ScenarioInput
from app.schemas.inventory import InventoryInput, InventoryPrediction
from app.services.inventory_service import predict_inventory
from app.services.scenario_service import to_inventory_input

router = APIRouter(tags=["inventory"])


@router.post("/predict/inventory", response_model=InventoryPrediction)
def inventory_prediction(payload: InventoryInput | ScenarioInput) -> InventoryPrediction:
    module_input = to_inventory_input(payload) if isinstance(payload, ScenarioInput) else payload
    return predict_inventory(module_input)
