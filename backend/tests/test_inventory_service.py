from app.schemas.inventory import InventoryInput
from app.services.inventory_service import predict_inventory


def _inventory_input(*, shortage_score: float, trolley_availability: float) -> InventoryInput:
    return InventoryInput(
        route_class="medium_haul",
        passenger_load=168,
        service_profile="standard",
        shortage_score=shortage_score,
        trolley_availability=trolley_availability,
        catering_complexity=4.3,
        turnaround_pressure=6.4,
        item_criticality=4.2,
        inventory_category="mixed_service",
    )


def test_inventory_risk_is_coherent_for_trolley_and_shortage_what_if_controls():
    low_pressure = predict_inventory(_inventory_input(shortage_score=0.0, trolley_availability=1.0))
    high_shortage = predict_inventory(_inventory_input(shortage_score=10.0, trolley_availability=1.0))
    low_trolley = predict_inventory(_inventory_input(shortage_score=0.0, trolley_availability=0.1))

    assert high_shortage.shortage_risk >= low_pressure.shortage_risk
    assert low_trolley.shortage_risk >= low_pressure.shortage_risk
    assert low_pressure.risk_level == "LOW"
