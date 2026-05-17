from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.demo import DemoFlightsResponse, DemoScenariosResponse, FlightDetail, RecomputeResponse, ScenarioInput
from app.services.scenario_service import (
    compute_scenario,
    get_demo_flight_detail,
    get_demo_flights,
    get_demo_scenarios_response,
)

router = APIRouter(tags=["demo"])


@router.get("/demo/flights", response_model=DemoFlightsResponse)
def demo_flights() -> DemoFlightsResponse:
    return get_demo_flights()


@router.get("/demo/scenarios", response_model=DemoScenariosResponse)
def demo_scenarios() -> DemoScenariosResponse:
    return get_demo_scenarios_response()


@router.get("/demo/flights/{flight_id}", response_model=FlightDetail)
def demo_flight_detail(flight_id: str) -> FlightDetail:
    try:
        return get_demo_flight_detail(flight_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/scenario/recompute", response_model=RecomputeResponse)
def recompute_scenario(payload: ScenarioInput) -> RecomputeResponse:
    return compute_scenario(payload)
