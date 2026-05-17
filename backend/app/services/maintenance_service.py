from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from app.core.config import get_settings
from app.schemas.maintenance import MaintenanceInput, MaintenancePrediction
from app.services.metadata_utils import rule_based_provenance, trained_ml_provenance


COMPONENT_RELATIONS = {
    "seat_power_unit": ["Seat power unit", "Seat row harness"],
    "galley_chiller": ["Galley chiller", "Galley power distribution"],
    "ife_display": ["IFE display", "IFE seat controller"],
    "lavatory_sensor": ["Lavatory occupancy sensor", "Lavatory control module"],
    "cabin_light_driver": ["Cabin light driver", "Ceiling power rail"],
}


def _bundle_path() -> Path:
    return get_settings().model_dir / "maintenance_bundle.joblib"


@lru_cache(maxsize=1)
def _load_bundle() -> dict | None:
    path = _bundle_path()
    try:
        if not path.exists():
            from app.training.train_maintenance_model import train_and_save_maintenance_model

            train_and_save_maintenance_model()
        return joblib.load(path)
    except Exception:
        return None


def _deterministic_risk(payload: MaintenanceInput) -> tuple[float, int, str]:
    score = (
        payload.wear_index / 100 * 0.34
        + payload.malfunction_count / 7 * 0.16
        + payload.malfunction_severity / 10 * 0.26
        + payload.environmental_stress / 10 * 0.12
        + min(payload.cycles_since_install / 4000, 1) * 0.08
        + min(payload.aircraft_age_cycles / 32000, 1) * 0.04
    )
    probability = float(min(max(score, 0.03), 0.97))
    remaining = int(
        max(
            0,
            round(
                58
                - probability * 44
                - payload.malfunction_severity * 1.5
                - payload.cycles_since_install / 260
            ),
        )
    )
    urgency = "OK"
    if probability >= 0.78 or remaining <= 5:
        urgency = "CRITICAL"
    elif probability >= 0.56 or remaining <= 12:
        urgency = "SOON"
    elif probability >= 0.35 or remaining <= 24:
        urgency = "PLAN"
    return probability, remaining, urgency


def _recommend_action(urgency: str, component_type: str) -> str:
    if urgency == "CRITICAL":
        return f"Dispatch maintenance technician to gate and reserve inspection slot for {component_type.replace('_', ' ')}."
    if urgency == "SOON":
        return f"Prepare targeted inspection and spare allocation for {component_type.replace('_', ' ')} on arrival."
    if urgency == "PLAN":
        return f"Schedule post-arrival diagnostic review for {component_type.replace('_', ' ')} and monitor follow-up flights."
    return "No immediate maintenance dispatch required; continue routine monitoring."


def _top_factors(payload: MaintenanceInput, ranked_features: list[str], remaining: int) -> list[str]:
    factor_map = {
        "malfunction_severity": "Reported malfunction severity is high.",
        "wear_index": "Wear index is elevated for the reported component.",
        "cycles_since_install": "Cycles since component installation are high.",
        "environmental_stress": "Environmental stress is accelerating degradation.",
        "aircraft_age_cycles": "The aircraft has accumulated high age-in-cycles exposure.",
        "humidity": "Humidity-related cabin conditions are contributing to component stress.",
        "cabin_temperature": "Cabin temperature is above the normal operating comfort range.",
        "passenger_load": "Passenger load increases usage-related wear.",
        "malfunction_count": "Multiple discrepancies were reported before arrival.",
        "flight_duration_hr": "Flight duration adds additional operating exposure.",
    }

    selected: list[str] = []
    for feature in ranked_features:
        if feature == "malfunction_severity" and payload.malfunction_severity < 5.5:
            continue
        if feature == "wear_index" and payload.wear_index < 65:
            continue
        if feature == "cycles_since_install" and payload.cycles_since_install < 1800:
            continue
        if feature == "environmental_stress" and payload.environmental_stress < 5:
            continue
        if feature == "aircraft_age_cycles" and payload.aircraft_age_cycles < 18000:
            continue
        if feature == "humidity" and payload.humidity < 55:
            continue
        if feature == "cabin_temperature" and payload.cabin_temperature < 27:
            continue
        if feature == "passenger_load" and payload.passenger_load < 170:
            continue
        if feature == "malfunction_count" and payload.malfunction_count < 2:
            continue
        if feature == "flight_duration_hr" and payload.flight_duration_hr < 2.5:
            continue
        text = factor_map.get(feature)
        if text and text not in selected:
            selected.append(text)
        if len(selected) == 3:
            break

    if remaining <= 8 and "Remaining flights are limited." not in selected:
        selected.append("Remaining flights are limited.")
    if not selected:
        selected.append("Observed maintenance indicators remain within a moderate operating envelope.")
    return selected[:3]


def predict_maintenance(payload: MaintenanceInput) -> MaintenancePrediction:
    bundle = _load_bundle()
    if bundle:
        frame = pd.DataFrame([payload.model_dump()])
        classifier = bundle["failure_model"]["estimator"]
        failure_metadata = bundle["failure_model"]["metadata"]
        urgency_classifier = bundle["urgency_model"]["estimator"]
        urgency_metadata = bundle["urgency_model"]["metadata"]
        regressor = bundle["rul_model"]["estimator"]
        rul_metadata = bundle["rul_model"]["metadata"]
        probability = float(classifier.predict_proba(frame)[0][1])
        urgency = str(urgency_classifier.predict(frame)[0])
        remaining = int(max(0, round(float(regressor.predict(frame)[0]))))
        confidence = float(max(probability, 1 - probability))
        ranked_features = list(
            dict.fromkeys(
                failure_metadata.get("top_features", [])
                + urgency_metadata.get("top_features", [])
                + rul_metadata.get("top_features", [])
            )
        )
        top_factors = _top_factors(payload, ranked_features, remaining)
        model_source = str(failure_metadata.get("selected_model", "Trained local maintenance model"))
        provenance = trained_ml_provenance(
            failure_metadata,
            "Failure probability is produced by a locally trained maintenance model; urgency and remaining flights are estimated by separately selected local models.",
        )
    else:
        probability, remaining, urgency = _deterministic_risk(payload)
        confidence = float(max(probability, 1 - probability))
        top_factors = _top_factors(
            payload,
            ["malfunction_severity", "wear_index", "cycles_since_install", "environmental_stress"],
            remaining,
        )
        model_source = "Deterministic fallback"
        provenance = rule_based_provenance(
            "Fallback maintenance scoring is active because the trained model artifact is unavailable. Risk is computed from transparent local rules."
        )

    anomaly_flag = (
        payload.malfunction_severity >= 7.5
        or (payload.wear_index >= 82 and payload.malfunction_count >= 2)
        or remaining <= 4
    )
    affected_components = COMPONENT_RELATIONS.get(payload.component_type, [payload.component_type.replace("_", " ").title()])
    explanation_reasons = [factor.rstrip(".") for factor in top_factors[:2]]
    if len(explanation_reasons) > 1:
        explanation = (
            f"Maintenance risk is elevated because {explanation_reasons[0].lower()} "
            f"and {explanation_reasons[1].lower()}."
        )
    else:
        explanation = f"Maintenance risk is elevated because {explanation_reasons[0].lower()}."

    return MaintenancePrediction(
        failure_probability=round(probability, 3),
        confidence=round(confidence, 3),
        remaining_flights_estimate=remaining,
        urgency_class=urgency,
        anomaly_flag=anomaly_flag,
        affected_components=affected_components,
        top_factors=top_factors,
        explanation=explanation,
        recommended_action=_recommend_action(urgency, payload.component_type),
        model_source=model_source,
        provenance=provenance,
    )
