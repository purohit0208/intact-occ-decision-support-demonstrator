from app.schemas.fusion import FusionInput
from app.schemas.bottleneck import BottleneckPrediction, BottleneckDistribution
from app.schemas.inventory import InventoryPrediction
from app.schemas.maintenance import MaintenancePrediction
from app.schemas.common import ProvenanceInfo
from app.services.fusion_service import predict_fusion

dummy_prov = ProvenanceInfo(
    category="rule_based_logic",
    label="test",
    summary="test"
)


def _maintenance_prediction(
    *,
    failure_probability: float,
    urgency_class: str,
    remaining_flights_estimate: int = 10,
    anomaly_flag: bool = False,
) -> MaintenancePrediction:
    return MaintenancePrediction(
        failure_probability=failure_probability,
        confidence=max(failure_probability, 1 - failure_probability),
        remaining_flights_estimate=remaining_flights_estimate,
        urgency_class=urgency_class,
        anomaly_flag=anomaly_flag,
        affected_components=["test_component"],
        top_factors=["test factor"],
        explanation="Test maintenance state",
        recommended_action="Test action",
        model_source="test",
        provenance=dummy_prov,
    )


def _inventory_prediction(*, shortage_risk: float, risk_level: str) -> InventoryPrediction:
    return InventoryPrediction(
        shortage_risk=shortage_risk,
        risk_level=risk_level,
        affected_service_area="economy",
        confidence=max(shortage_risk, 1 - shortage_risk),
        trolley_status="OK",
        top_factors=["test factor"],
        recommendation="None",
        explanation="Test inventory state",
        model_source="test",
        provenance=dummy_prov,
    )


def _bottleneck_prediction(
    *,
    maintenance: float,
    catering: float,
    cleaning: float,
    boarding: float,
    refueling: float,
    dominant_bottleneck: str,
) -> BottleneckPrediction:
    distribution = BottleneckDistribution(
        Maintenance=maintenance,
        Catering=catering,
        Cleaning=cleaning,
        Boarding=boarding,
        Refueling=refueling,
    )
    return BottleneckPrediction(
        probabilities=distribution,
        dominant_bottleneck=dominant_bottleneck,
        confidence=max(maintenance, catering, cleaning, boarding, refueling),
        top_contributing_factors=["test factor"],
        explanation="Test bottleneck state",
        recommended_response="Test response",
        model_source="test",
        provenance=dummy_prov,
    )

def test_predict_fusion_critical_maintenance():
    maintenance = _maintenance_prediction(
        failure_probability=0.9,
        urgency_class="CRITICAL",
        remaining_flights_estimate=0,
        anomaly_flag=True,
    )
    inventory = _inventory_prediction(shortage_risk=0.1, risk_level="LOW")
    bottleneck = _bottleneck_prediction(
        maintenance=0.1,
        catering=0.1,
        cleaning=0.2,
        boarding=0.5,
        refueling=0.1,
        dominant_bottleneck="Boarding",
    )

    payload = FusionInput(
        passenger_load=150,
        arrival_delay=60,
        gate_congestion=8,
        assistance_request=False,
        assistance_equipment_confirmed=False,
        maintenance=maintenance,
        inventory=inventory,
        bottleneck=bottleneck
    )
    
    result = predict_fusion(payload)
    
    assert result.alert_level == "Critical"
    assert result.at_risk is True
    assert result.readiness_score < 70
    
    teams = [a.team for a in result.action_queue]
    assert "Line Maintenance" in teams
    assert "Maintenance Control" in teams

def test_predict_fusion_compounding_cross_domain_risk_adds_occ_action():
    maintenance = _maintenance_prediction(failure_probability=0.82, urgency_class="CRITICAL", remaining_flights_estimate=2)
    inventory = _inventory_prediction(shortage_risk=0.86, risk_level="HIGH")
    bottleneck = _bottleneck_prediction(
        maintenance=0.68,
        catering=0.1,
        cleaning=0.07,
        boarding=0.1,
        refueling=0.05,
        dominant_bottleneck="Maintenance",
    )

    payload = FusionInput(
        passenger_load=178,
        arrival_delay=24,
        gate_congestion=7.8,
        assistance_request=False,
        assistance_equipment_confirmed=False,
        maintenance=maintenance,
        inventory=inventory,
        bottleneck=bottleneck
    )

    result = predict_fusion(payload)

    assert any(item.label == "Compounding cross-domain risk" for item in result.readiness_breakdown)
    assert any("Compounding cross-domain risk is elevated" in item for item in result.alert_summary)
    assert any(action.description == "Coordinate cross-team turnaround response before arrival." for action in result.action_queue)
    assert result.alert_level in {"Priority", "Critical"}
    assert result.at_risk is True


def test_predict_fusion_normal_scenario():
    maintenance = _maintenance_prediction(failure_probability=0.05, urgency_class="OK")
    inventory = _inventory_prediction(shortage_risk=0.0, risk_level="LOW")
    bottleneck = _bottleneck_prediction(
        maintenance=0.05,
        catering=0.3,
        cleaning=0.4,
        boarding=0.1,
        refueling=0.15,
        dominant_bottleneck="Cleaning",
    )

    payload = FusionInput(
        passenger_load=120,
        arrival_delay=0,
        gate_congestion=1,
        assistance_request=True,
        assistance_equipment_confirmed=True,
        maintenance=maintenance,
        inventory=inventory,
        bottleneck=bottleneck
    )

    result = predict_fusion(payload)

    assert result.alert_level == "Routine", f"Expected Routine, but got {result.alert_level} with criticality {result.criticality_score}"
    assert result.at_risk is False
    assert result.readiness_score > 70
    assert all(item.label != "Compounding cross-domain risk" for item in result.readiness_breakdown)


def test_predict_fusion_readiness_decreases_with_worse_maintenance_signal():
    inventory = _inventory_prediction(shortage_risk=0.18, risk_level="LOW")
    bottleneck = _bottleneck_prediction(
        maintenance=0.18,
        catering=0.24,
        cleaning=0.2,
        boarding=0.28,
        refueling=0.1,
        dominant_bottleneck="Boarding",
    )
    baseline = FusionInput(
        passenger_load=130,
        arrival_delay=4,
        gate_congestion=3.0,
        assistance_request=False,
        assistance_equipment_confirmed=False,
        maintenance=_maintenance_prediction(failure_probability=0.12, urgency_class="OK"),
        inventory=inventory,
        bottleneck=bottleneck,
    )
    degraded = baseline.model_copy(
        update={"maintenance": _maintenance_prediction(failure_probability=0.82, urgency_class="CRITICAL")}
    )

    assert predict_fusion(degraded).readiness_score < predict_fusion(baseline).readiness_score


def test_predict_fusion_assistance_confirmation_removes_readiness_penalty():
    maintenance = _maintenance_prediction(failure_probability=0.08, urgency_class="OK")
    inventory = _inventory_prediction(shortage_risk=0.16, risk_level="LOW")
    bottleneck = _bottleneck_prediction(
        maintenance=0.12,
        catering=0.18,
        cleaning=0.2,
        boarding=0.4,
        refueling=0.1,
        dominant_bottleneck="Boarding",
    )
    pending = FusionInput(
        passenger_load=110,
        arrival_delay=2,
        gate_congestion=3.5,
        assistance_request=True,
        assistance_equipment_confirmed=False,
        maintenance=maintenance,
        inventory=inventory,
        bottleneck=bottleneck,
    )
    confirmed = pending.model_copy(update={"assistance_equipment_confirmed": True})

    pending_result = predict_fusion(pending)
    confirmed_result = predict_fusion(confirmed)

    assert confirmed_result.readiness_score > pending_result.readiness_score
    assert any(item.label == "Passenger assistance readiness" for item in pending_result.readiness_breakdown)
    assert all(item.label != "Passenger assistance readiness" for item in confirmed_result.readiness_breakdown)
