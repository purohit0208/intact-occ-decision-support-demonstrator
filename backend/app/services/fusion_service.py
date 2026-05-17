from __future__ import annotations

from app.schemas.fusion import ActionItem, FusionInput, FusionPrediction, ReadinessFactor
from app.services.metadata_utils import rule_based_provenance


PRIORITY_ORDER = {"P1": 0, "P2": 1, "P3": 2, "P4": 3}


def _maintenance_display_label(urgency_class: str) -> str:
    return {
        "OK": "LOW",
        "PLAN": "ELEVATED",
        "SOON": "HIGH",
        "CRITICAL": "CRITICAL",
    }.get(urgency_class, urgency_class)


def _compounding_domains(payload: FusionInput, bottleneck_max: float) -> list[str]:
    domains: list[str] = []

    if payload.maintenance.urgency_class == "CRITICAL" or payload.maintenance.failure_probability >= 0.72:
        domains.append("maintenance risk")
    if payload.inventory.risk_level == "HIGH" or payload.inventory.shortage_risk >= 0.78:
        domains.append("inventory risk")
    if bottleneck_max >= 0.62:
        domains.append("bottleneck pressure")
    if payload.gate_congestion >= 7.0 or payload.arrival_delay >= 20:
        domains.append("turnaround margin compression")

    return domains


def _build_actions(payload: FusionInput, compounding_domains: list[str]) -> list[ActionItem]:
    actions: list[ActionItem] = []
    maintenance = payload.maintenance
    inventory = payload.inventory
    bottleneck = payload.bottleneck

    if maintenance.urgency_class in {"SOON", "CRITICAL"}:
        actions.append(
            ActionItem(
                priority="P1" if maintenance.urgency_class == "CRITICAL" else "P2",
                team="Line Maintenance",
                description="Dispatch maintenance technician to assigned gate.",
                rationale=maintenance.explanation,
                expected_impact="Reduces the chance of maintenance-driven turnaround disruption.",
            )
        )
        actions.append(
            ActionItem(
                priority="P2",
                team="Maintenance Control",
                description="Reserve spare component and post-arrival inspection slot.",
                rationale="Remaining useful life is constrained for the reported cabin component.",
                expected_impact="Improves maintenance readiness before chocks-on.",
            )
        )

    if inventory.risk_level in {"ELEVATED", "HIGH"}:
        actions.append(
            ActionItem(
                priority="P1" if inventory.risk_level == "HIGH" else "P2",
                team="Catering and Cabin Services",
                description="Replace or top up trolley allocation before arrival.",
                rationale=inventory.explanation,
                expected_impact="Lowers service disruption risk and protects boarding readiness.",
            )
        )

    if bottleneck.dominant_bottleneck == "Catering":
        actions.append(
            ActionItem(
                priority="P2",
                team="Catering Supervisor",
                description="Confirm catering uplift sequence and protect the affected service area.",
                rationale="Catering is the leading bottleneck in the current scenario and inventory pressure is reducing turnaround flexibility.",
                expected_impact="Improves service readiness and reduces the chance of catering-driven delay.",
            )
        )

    if bottleneck.dominant_bottleneck == "Cleaning":
        actions.append(
            ActionItem(
                priority="P3",
                team="Cabin Cleaning",
                description="Pre-brief cabin cleaning team on compressed turnaround timing.",
                rationale=bottleneck.explanation,
                expected_impact="Reduces the risk of cleaning-related knock-on delay under higher cabin turnover.",
            )
        )

    if payload.assistance_request and not payload.assistance_equipment_confirmed:
        actions.append(
            ActionItem(
                priority="P1",
                team="PRM Assistance Team",
                description="Pre-position wheelchair or assistance equipment and confirm dispatch.",
                rationale="Active passenger assistance request is not yet matched with confirmed readiness.",
                expected_impact="Improves passenger assistance readiness and reduces stand-side coordination delay.",
            )
        )

    if payload.arrival_delay >= 15 or payload.gate_congestion >= 6:
        actions.append(
            ActionItem(
                priority="P2",
                team="Gate Coordination",
                description="Allocate turnaround buffer and brief gate coordinator.",
                rationale="Arrival delay and gate congestion compress available turnaround margin.",
                expected_impact="Supports proactive stand coordination under time pressure.",
            )
        )

    if compounding_domains:
        actions.append(
            ActionItem(
                priority="P1" if len(compounding_domains) >= 3 else "P2",
                team="OCC Supervisor",
                description="Coordinate cross-team turnaround response before arrival.",
                rationale=(
                    "Multiple severe domains are active simultaneously: "
                    + ", ".join(compounding_domains)
                    + "."
                ),
                expected_impact="Improves cross-functional sequencing under compounded turnaround risk.",
            )
        )

    if bottleneck.dominant_bottleneck == "Boarding":
        actions.append(
            ActionItem(
                priority="P3",
                team="Turnaround Duty Manager",
                description="Monitor boarding queue and prepare contingency stand sequencing.",
                rationale=bottleneck.explanation,
                expected_impact="Improves visibility for boarding-related knock-on delays.",
            )
        )

        if payload.passenger_load >= 170:
            actions.append(
                ActionItem(
                    priority="P2",
                    team="Gate Team",
                    description="Prepare boarding lane management and early gate briefing.",
                    rationale="High passenger load increases boarding pressure in the current scenario.",
                    expected_impact="Supports steadier passenger flow and reduces stand-side queueing risk.",
                )
            )

    if bottleneck.dominant_bottleneck == "Refueling":
        actions.append(
            ActionItem(
                priority="P3",
                team="Ramp and Fuel Coordination",
                description="Confirm refueling slot and cross-check arrival stand access.",
                rationale=bottleneck.explanation,
                expected_impact="Protects fuel sequencing during a compressed turnaround window.",
            )
        )

    actions.append(
        ActionItem(
            priority="P4",
            team="OCC Supervisor",
            description="Maintain operator review of recommended actions and reassess after aircraft arrival.",
            rationale="This demonstrator provides decision support only and keeps the operator in the loop.",
            expected_impact="Ensures conservative human oversight of the simulated operator-support outputs.",
        )
    )

    deduped: list[ActionItem] = []
    seen: set[tuple[str, str]] = set()
    for action in actions:
        key = (action.team, action.description)
        if key not in seen:
            seen.add(key)
            deduped.append(action)

    deduped.sort(key=lambda action: PRIORITY_ORDER[action.priority])
    return deduped


def _build_readiness_breakdown(
    payload: FusionInput,
    maintenance_penalty: float,
    failure_penalty: float,
    inventory_penalty: float,
    bottleneck_penalty: float,
    congestion_penalty: float,
    delay_penalty: float,
    assistance_penalty: float,
    compounding_penalty: float,
) -> list[ReadinessFactor]:
    breakdown = [
        ReadinessFactor(
            label="Maintenance urgency",
            impact=round(maintenance_penalty, 1),
            detail=f"Maintenance status {_maintenance_display_label(payload.maintenance.urgency_class)} lowers readiness in a transparent rule-based way.",
        ),
        ReadinessFactor(
            label="Predicted maintenance failure risk",
            impact=round(failure_penalty, 1),
            detail="Higher failure probability reduces readiness before arrival.",
        ),
        ReadinessFactor(
            label="Inventory and trolley risk",
            impact=round(inventory_penalty, 1),
            detail=f"Inventory status is currently assessed as {payload.inventory.risk_level.lower()}.",
        ),
        ReadinessFactor(
            label="Dominant bottleneck pressure",
            impact=round(bottleneck_penalty, 1),
            detail=f"{payload.bottleneck.dominant_bottleneck} is the leading turnaround bottleneck in this scenario.",
        ),
        ReadinessFactor(
            label="Gate congestion",
            impact=round(congestion_penalty, 1),
            detail="Gate congestion reduces operational margin around stand coordination.",
        ),
        ReadinessFactor(
            label="Arrival delay",
            impact=round(delay_penalty, 1),
            detail="Arrival delay compresses the remaining turnaround window.",
        ),
    ]

    if assistance_penalty > 0:
        breakdown.append(
            ReadinessFactor(
                label="Passenger assistance readiness",
                impact=round(assistance_penalty, 1),
                detail="Active assistance remains unconfirmed, so readiness is reduced until equipment dispatch is secured.",
            )
        )

    if compounding_penalty > 0:
        breakdown.append(
            ReadinessFactor(
                label="Compounding cross-domain risk",
                impact=round(compounding_penalty, 1),
                detail="Multiple severe indicators are active simultaneously and reduce the remaining recovery margin.",
            )
        )

    return sorted(breakdown, key=lambda item: item.impact, reverse=True)


def predict_fusion(payload: FusionInput) -> FusionPrediction:
    maintenance_penalties = {"OK": 3, "PLAN": 10, "SOON": 18, "CRITICAL": 30}
    bottleneck_max = max(payload.bottleneck.probabilities.model_dump().values())
    maintenance_penalty = float(maintenance_penalties[payload.maintenance.urgency_class])
    failure_penalty = payload.maintenance.failure_probability * 9
    inventory_penalty = payload.inventory.shortage_risk * 11
    bottleneck_penalty = bottleneck_max * 14
    congestion_penalty = payload.gate_congestion * 1.25

    if payload.arrival_delay <= 15:
        delay_penalty = payload.arrival_delay * 0.26
    else:
        delay_penalty = (15 * 0.26) + min(14.0, ((payload.arrival_delay - 15) ** 1.12) * 0.28)
    delay_penalty = min(delay_penalty, 18.0)

    assistance_penalty = 9.0 if payload.assistance_request and not payload.assistance_equipment_confirmed else 0.0

    compounding_domains = _compounding_domains(payload, bottleneck_max)
    compounding_penalty = {0: 0.0, 1: 0.0, 2: 4.0, 3: 7.0}.get(len(compounding_domains), 10.0)

    readiness = 100.0
    readiness -= maintenance_penalty
    readiness -= failure_penalty
    readiness -= inventory_penalty
    readiness -= bottleneck_penalty
    readiness -= congestion_penalty
    readiness -= delay_penalty
    readiness -= assistance_penalty
    readiness -= compounding_penalty
    readiness = max(5.0, min(99.0, readiness))

    criticality = min(
        100.0,
        100 - readiness
        + payload.maintenance.failure_probability * 12
        + payload.inventory.shortage_risk * 8
        + bottleneck_max * 13,
    )

    if criticality >= 80 or readiness <= 38:
        alert_level = "Critical"
    elif criticality >= 61 or readiness <= 56:
        alert_level = "Priority"
    elif criticality >= 42 or readiness <= 74:
        alert_level = "Watch"
    else:
        alert_level = "Routine"

    at_risk = readiness < 70 or alert_level in {"Priority", "Critical"}

    alert_summary: list[str] = []
    if payload.maintenance.urgency_class in {"SOON", "CRITICAL"}:
        alert_summary.append(
            "Maintenance bottleneck risk is elevated due to high malfunction severity and low remaining useful life."
        )
    if payload.inventory.risk_level in {"ELEVATED", "HIGH"}:
        alert_summary.append(
            "Inventory alert is triggered because predicted shortage risk is elevated under the current service and replenishment conditions."
        )
    if payload.assistance_request and not payload.assistance_equipment_confirmed:
        alert_summary.append(
            "Passenger assistance readiness is incomplete because active assistance has not yet been matched with confirmed equipment availability."
        )
    if payload.bottleneck.dominant_bottleneck == "Boarding":
        alert_summary.append("Boarding-related delay risk rises under high passenger load and elevated gate congestion.")
    if payload.bottleneck.dominant_bottleneck == "Refueling":
        alert_summary.append("Refueling coordination should be monitored because available turnaround margin is compressed.")
    if compounding_penalty > 0:
        alert_summary.append(
            "Compounding cross-domain risk is elevated because multiple severe indicators are active simultaneously."
        )

    if not alert_summary:
        alert_summary.append("Current scenario remains within a manageable readiness envelope with no immediate critical alerts.")

    delay_risk = min(
        28.0,
        2.6
        + payload.maintenance.failure_probability * 7.2
        + payload.inventory.shortage_risk * 5.0
        + bottleneck_max * 8.3
        + payload.arrival_delay * 0.06,
    )
    expected_benefit = min(
        12.0,
        1.1
        + (0.9 if payload.assistance_request and not payload.assistance_equipment_confirmed else 0)
        + payload.maintenance.failure_probability * 2.8
        + payload.inventory.shortage_risk * 2.4
        + bottleneck_max * 3.1,
    )

    return FusionPrediction(
        readiness_score=round(readiness, 1),
        criticality_score=round(criticality, 1),
        alert_level=alert_level,
        at_risk=at_risk,
        alert_summary=alert_summary,
        readiness_breakdown=_build_readiness_breakdown(
            payload,
            maintenance_penalty,
            failure_penalty,
            inventory_penalty,
            bottleneck_penalty,
            congestion_penalty,
            delay_penalty,
            assistance_penalty,
            compounding_penalty,
        ),
        action_queue=_build_actions(payload, compounding_domains),
        expected_delay_risk_min=round(delay_risk, 1),
        expected_benefit_min=round(expected_benefit, 1),
        proactive_vs_reactive_delta_min=round(expected_benefit + 1.2, 1),
        explanation=(
            "The fused readiness assessment combines maintenance, inventory, bottleneck, congestion, and passenger assistance signals for operator review."
        ),
        provenance=rule_based_provenance(
            "Readiness score, alert prioritization, and action queue are produced by a transparent rule-based fusion layer operating on module outputs and scenario state."
        ),
    )
