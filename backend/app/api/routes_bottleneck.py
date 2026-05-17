from __future__ import annotations

from fastapi import APIRouter

from app.schemas.demo import ScenarioInput
from app.schemas.bottleneck import BottleneckInput, BottleneckPrediction
from app.services.bottleneck_service import predict_bottleneck
from app.services.scenario_service import to_bottleneck_input

router = APIRouter(tags=["bottleneck"])


@router.post("/predict/bottleneck", response_model=BottleneckPrediction)
def bottleneck_prediction(payload: BottleneckInput | ScenarioInput) -> BottleneckPrediction:
    module_input = to_bottleneck_input(payload) if isinstance(payload, ScenarioInput) else payload
    return predict_bottleneck(module_input)
