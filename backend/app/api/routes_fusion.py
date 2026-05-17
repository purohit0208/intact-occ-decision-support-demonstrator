from __future__ import annotations

from fastapi import APIRouter

from app.schemas.demo import ScenarioInput
from app.schemas.fusion import FusionInput, FusionPrediction
from app.services.fusion_service import predict_fusion
from app.services.scenario_service import compute_scenario

router = APIRouter(tags=["fusion"])


@router.post("/predict/fusion", response_model=FusionPrediction)
def fusion_prediction(payload: FusionInput | ScenarioInput) -> FusionPrediction:
    if isinstance(payload, ScenarioInput):
        return compute_scenario(payload).fusion
    return predict_fusion(payload)
