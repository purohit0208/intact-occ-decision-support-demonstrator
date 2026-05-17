from __future__ import annotations

from functools import lru_cache

from app.schemas.bottleneck import BottleneckInput
from app.schemas.demo import (
    DemoFlightsResponse,
    DemoScenariosResponse,
    FlightDetail,
    FlightSummary,
    RecomputeResponse,
    ScenarioInput,
)
from app.schemas.fusion import FusionInput
from app.schemas.inventory import InventoryInput
from app.schemas.maintenance import MaintenanceInput
from app.services.bottleneck_service import predict_bottleneck
from app.services.fusion_service import predict_fusion
from app.services.inventory_service import predict_inventory
from app.services.maintenance_service import predict_maintenance


def _with_assistance_status(scenario: ScenarioInput) -> ScenarioInput:
    if not scenario.assistance_request:
        return scenario.model_copy(
            update={
                "assistance_equipment_confirmed": False,
                "assistance_localization_status": "Not required",
            }
        )
    if scenario.assistance_equipment_confirmed:
        return scenario.model_copy(update={"assistance_localization_status": "Equipment confirmed"})
    return scenario.model_copy(update={"assistance_localization_status": "Pending gate coordination"})


def to_maintenance_input(scenario: ScenarioInput) -> MaintenanceInput:
    return MaintenanceInput(
        aircraft_type=scenario.aircraft_type,
        component_type=scenario.component_type,
        aircraft_age_cycles=scenario.aircraft_age_cycles,
        flight_duration_hr=scenario.flight_duration_hr,
        cabin_temperature=scenario.cabin_temperature,
        humidity=scenario.humidity,
        passenger_load=scenario.passenger_load,
        cycles_since_install=scenario.cycles_since_install,
        wear_index=scenario.wear_index,
        malfunction_count=scenario.malfunction_count,
        malfunction_severity=scenario.malfunction_severity,
        environmental_stress=scenario.environmental_stress,
    )


def to_inventory_input(scenario: ScenarioInput) -> InventoryInput:
    return InventoryInput(
        route_class=scenario.route_class,
        passenger_load=scenario.passenger_load,
        service_profile=scenario.service_profile,
        shortage_score=scenario.inventory_shortage_score,
        trolley_availability=scenario.trolley_availability,
        catering_complexity=scenario.catering_complexity,
        turnaround_pressure=scenario.turnaround_pressure,
        item_criticality=scenario.item_criticality,
        inventory_category=scenario.inventory_category,
    )


def to_bottleneck_input(scenario: ScenarioInput) -> BottleneckInput:
    return BottleneckInput(
        passenger_load=scenario.passenger_load,
        arrival_delay=scenario.arrival_delay,
        gate_congestion=scenario.gate_congestion,
        malfunction_count=scenario.malfunction_count,
        malfunction_severity=scenario.malfunction_severity,
        inventory_shortage=scenario.inventory_shortage_score,
        aircraft_type=scenario.aircraft_type,
        route_class=scenario.route_class,
        assistance_request=scenario.assistance_request,
        refueling_required=scenario.refueling_required,
        weather_disturbance=scenario.weather_disturbance,
    )


def to_fusion_input(
    scenario: ScenarioInput,
    maintenance=None,
    inventory=None,
    bottleneck=None,
) -> FusionInput:
    maintenance = maintenance or predict_maintenance(to_maintenance_input(scenario))
    inventory = inventory or predict_inventory(to_inventory_input(scenario))
    bottleneck = bottleneck or predict_bottleneck(to_bottleneck_input(scenario))
    return FusionInput(
        passenger_load=scenario.passenger_load,
        arrival_delay=scenario.arrival_delay,
        gate_congestion=scenario.gate_congestion,
        assistance_request=scenario.assistance_request,
        assistance_equipment_confirmed=scenario.assistance_equipment_confirmed,
        maintenance=maintenance,
        inventory=inventory,
        bottleneck=bottleneck,
    )


@lru_cache(maxsize=1)
def get_demo_scenarios() -> tuple[ScenarioInput, ...]:
    return tuple(
        _with_assistance_status(item)
        for item in (
            ScenarioInput(
                id="flt-maint-critical",
                flight_number="DEMO-01",
                aircraft_type="A320neo",
                route="FRA -> BCN",
                route_class="medium_haul",
                eta="16:25",
                gate="A12",
                passenger_load=168,
                arrival_delay=18,
                gate_congestion=6.8,
                assistance_request=False,
                inventory_shortage_score=3.1,
                trolley_availability=0.78,
                service_profile="standard",
                catering_complexity=4.3,
                turnaround_pressure=6.4,
                item_criticality=4.2,
                inventory_category="mixed_service",
                malfunction_count=4,
                malfunction_severity=8.6,
                component_type="galley_chiller",
                aircraft_age_cycles=24100,
                flight_duration_hr=2.1,
                cabin_temperature=28.2,
                humidity=47,
                cycles_since_install=3520,
                wear_index=84,
                environmental_stress=7.1,
                weather_disturbance=2,
                refueling_required=True,
                cabin_report_notes=[
                    "Galley cooling degradation reported by cabin crew before descent.",
                    "Secondary power reset unsuccessful during cruise.",
                ],
                reported_components=["Galley chiller", "Galley power distribution"],
            ),
            ScenarioInput(
                id="flt-inventory-service",
                flight_number="DEMO-02",
                aircraft_type="A321",
                route="CGN -> PMI",
                route_class="medium_haul",
                eta="16:40",
                gate="B06",
                passenger_load=194,
                arrival_delay=9,
                gate_congestion=5.1,
                assistance_request=False,
                inventory_shortage_score=7.9,
                trolley_availability=0.34,
                service_profile="high_turnover",
                catering_complexity=7.8,
                turnaround_pressure=6.1,
                item_criticality=7.2,
                inventory_category="meal",
                malfunction_count=1,
                malfunction_severity=2.8,
                component_type="seat_power_unit",
                aircraft_age_cycles=18600,
                flight_duration_hr=2.4,
                cabin_temperature=24.5,
                humidity=33,
                cycles_since_install=1850,
                wear_index=46,
                environmental_stress=3.6,
                weather_disturbance=1,
                refueling_required=True,
                cabin_report_notes=[
                    "Cabin crew flagged missing trolley pairing for inbound service set.",
                    "Forward galley inventory mismatch reported in structured message.",
                ],
                reported_components=["Service trolley set"],
            ),
            ScenarioInput(
                id="flt-assistance-readiness",
                flight_number="DEMO-03",
                aircraft_type="E195-E2",
                route="VIE -> MUC",
                route_class="short_haul",
                eta="16:55",
                gate="C03",
                passenger_load=101,
                arrival_delay=4,
                gate_congestion=4.8,
                assistance_request=True,
                assistance_equipment_confirmed=False,
                inventory_shortage_score=2.4,
                trolley_availability=0.81,
                service_profile="standard",
                catering_complexity=3.2,
                turnaround_pressure=4.6,
                item_criticality=3.4,
                inventory_category="wheelchair_kit",
                malfunction_count=0,
                malfunction_severity=1.2,
                component_type="lavatory_sensor",
                aircraft_age_cycles=9200,
                flight_duration_hr=0.9,
                cabin_temperature=22.0,
                humidity=31,
                cycles_since_install=640,
                wear_index=29,
                environmental_stress=2.1,
                weather_disturbance=0,
                refueling_required=False,
                cabin_report_notes=[
                    "Wheelchair assistance request transmitted before landing.",
                    "Ground confirmation not yet received in the OCC workflow.",
                ],
                reported_components=["Passenger assistance request"],
            ),
            ScenarioInput(
                id="flt-normal-lowrisk",
                flight_number="DEMO-04",
                aircraft_type="A320neo",
                route="ZRH -> HAM",
                route_class="short_haul",
                eta="17:05",
                gate="A04",
                passenger_load=132,
                arrival_delay=2,
                gate_congestion=2.7,
                assistance_request=False,
                inventory_shortage_score=1.8,
                trolley_availability=0.88,
                service_profile="standard",
                catering_complexity=2.8,
                turnaround_pressure=3.1,
                item_criticality=2.7,
                inventory_category="mixed_service",
                malfunction_count=0,
                malfunction_severity=0.8,
                component_type="cabin_light_driver",
                aircraft_age_cycles=10800,
                flight_duration_hr=1.3,
                cabin_temperature=22.6,
                humidity=29,
                cycles_since_install=540,
                wear_index=24,
                environmental_stress=1.8,
                weather_disturbance=0,
                refueling_required=True,
                cabin_report_notes=["No significant pre-arrival cabin discrepancies transmitted."],
                reported_components=["Routine cabin report only"],
            ),
            ScenarioInput(
                id="flt-composite-multirisk",
                flight_number="DEMO-05",
                aircraft_type="B737-800",
                route="DUB -> BER",
                route_class="medium_haul",
                eta="17:20",
                gate="B11",
                passenger_load=179,
                arrival_delay=23,
                gate_congestion=7.4,
                assistance_request=True,
                assistance_equipment_confirmed=True,
                inventory_shortage_score=5.9,
                trolley_availability=0.52,
                service_profile="business_priority",
                catering_complexity=6.8,
                turnaround_pressure=7.2,
                item_criticality=6.5,
                inventory_category="beverage",
                malfunction_count=2,
                malfunction_severity=5.7,
                component_type="ife_display",
                aircraft_age_cycles=21400,
                flight_duration_hr=2.1,
                cabin_temperature=26.7,
                humidity=44,
                cycles_since_install=2420,
                wear_index=63,
                environmental_stress=5.2,
                weather_disturbance=3.4,
                refueling_required=True,
                cabin_report_notes=[
                    "Mixed pre-arrival signals include IFE faults and partial trolley mismatch.",
                    "Gate occupancy forecast indicates elevated stand pressure.",
                ],
                reported_components=["IFE display", "Beverage trolley set", "Passenger assistance equipment"],
            ),
        )
    )


def compute_scenario(scenario: ScenarioInput) -> RecomputeResponse:
    scenario = _with_assistance_status(scenario)
    maintenance = predict_maintenance(to_maintenance_input(scenario))
    inventory = predict_inventory(to_inventory_input(scenario))
    bottleneck = predict_bottleneck(to_bottleneck_input(scenario))
    fusion = predict_fusion(to_fusion_input(scenario, maintenance=maintenance, inventory=inventory, bottleneck=bottleneck))

    return RecomputeResponse(
        scenario=scenario,
        maintenance=maintenance,
        inventory=inventory,
        bottleneck=bottleneck,
        fusion=fusion,
    )


def _summary_from_response(response: RecomputeResponse) -> FlightSummary:
    scenario = response.scenario
    assistance_status = (
        "Not required"
        if not scenario.assistance_request
        else "Confirmed"
        if scenario.assistance_equipment_confirmed
        else "Pending"
    )
    return FlightSummary(
        id=scenario.id,
        flight_number=scenario.flight_number,
        aircraft_type=scenario.aircraft_type,
        route=scenario.route,
        eta=scenario.eta,
        gate=scenario.gate,
        arrival_delay=scenario.arrival_delay,
        readiness_score=response.fusion.readiness_score,
        dominant_bottleneck=response.bottleneck.dominant_bottleneck,
        maintenance_urgency=response.maintenance.urgency_class,
        inventory_alert_status=response.inventory.risk_level,
        passenger_assistance_status=assistance_status,
        alert_level=response.fusion.alert_level,
        at_risk=response.fusion.at_risk,
    )


def get_demo_flights() -> DemoFlightsResponse:
    responses = [compute_scenario(scenario) for scenario in get_demo_scenarios()]
    return DemoFlightsResponse(flights=[_summary_from_response(response) for response in responses])


def get_demo_scenarios_response() -> DemoScenariosResponse:
    return DemoScenariosResponse(scenarios=list(get_demo_scenarios()))


def get_demo_flight_detail(flight_id: str) -> FlightDetail:
    for scenario in get_demo_scenarios():
        if scenario.id == flight_id:
            response = compute_scenario(scenario)
            return FlightDetail(
                scenario=response.scenario,
                maintenance=response.maintenance,
                inventory=response.inventory,
                bottleneck=response.bottleneck,
                fusion=response.fusion,
            )
    raise KeyError(f"Unknown flight id: {flight_id}")
