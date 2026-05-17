from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.core.config import get_settings
from app.schemas.inventory import InventoryInput, InventoryPrediction
from app.services.metadata_utils import rule_based_provenance, trained_ml_provenance


def _bundle_path() -> Path:
    return get_settings().model_dir / "inventory_bundle.joblib"


@lru_cache(maxsize=1)
def _load_bundle() -> dict | None:
    path = _bundle_path()
    try:
        if not path.exists():
            from app.training.train_inventory_model import train_and_save_inventory_model

            train_and_save_inventory_model()
        return joblib.load(path)
    except Exception:
        return None


def _fallback(payload: InventoryInput) -> tuple[float, str]:
    score = (
        payload.shortage_score / 10 * 0.24
        + (1 - payload.trolley_availability) * 0.28
        + payload.catering_complexity / 10 * 0.14
        + payload.turnaround_pressure / 10 * 0.16
        + payload.item_criticality / 10 * 0.12
        + (0.07 if payload.route_class == "long_haul" else 0.0)
    )
    risk = float(min(max(score, 0.03), 0.97))
    return risk, _risk_level_from_score(risk)


def _risk_level_from_score(shortage_risk: float) -> str:
    if shortage_risk >= 0.75:
        return "HIGH"
    if shortage_risk >= 0.45:
        return "ELEVATED"
    return "LOW"


def _affected_area(payload: InventoryInput) -> str:
    if payload.inventory_category != "mixed_service":
        return payload.inventory_category
    if payload.service_profile == "business_priority":
        return "premium_cabin"
    if payload.route_class == "long_haul":
        return "long_haul_service"
    return "standard_service"


def _recommendation(level: str, area: str, trolley_availability: float) -> str:
    if level == "HIGH" and trolley_availability < 0.45:
        return f"Replace or reassign trolley set for {area.replace('_', ' ')} before arrival."
    if level in {"HIGH", "ELEVATED"}:
        return f"Alert catering supervisor and top up {area.replace('_', ' ')} inventory prior to turnaround start."
    return "Maintain current allocation and monitor for any late changes in service demand."


def _top_factors(payload: InventoryInput, ranked_features: list[str]) -> list[str]:
    candidate_map = {
        "trolley_availability": "Trolley availability is below the preferred service threshold.",
        "shortage_score": "Pre-arrival shortage indicators are elevated.",
        "turnaround_pressure": "Turnaround pressure reduces replenishment margin.",
        "item_criticality": "The affected inventory class has higher service criticality.",
        "catering_complexity": "Catering complexity increases the chance of mismatch or incomplete uplift.",
        "passenger_load": "Passenger load increases expected service consumption.",
        "route_class": f"Route class is {payload.route_class.replace('_', ' ')}.",
        "service_profile": f"Service profile is {payload.service_profile.replace('_', ' ')}.",
        "inventory_category": f"The active inventory category is {payload.inventory_category.replace('_', ' ')}.",
    }

    gated: list[str] = []
    for feature in ranked_features:
        if feature == "trolley_availability" and payload.trolley_availability >= 0.65:
            continue
        if feature == "shortage_score" and payload.shortage_score < 4.5:
            continue
        if feature == "turnaround_pressure" and payload.turnaround_pressure < 5:
            continue
        if feature == "item_criticality" and payload.item_criticality < 5:
            continue
        if feature == "catering_complexity" and payload.catering_complexity < 5:
            continue
        text = candidate_map.get(feature)
        if text and text not in gated:
            gated.append(text)
        if len(gated) == 3:
            break

    if not gated:
        gated.append("Observed inventory and service indicators remain within the normal planning envelope.")
    return gated


def predict_inventory(payload: InventoryInput) -> InventoryPrediction:
    bundle = _load_bundle()
    affected_area = _affected_area(payload)
    if bundle:
        frame = pd.DataFrame([payload.model_dump()])
        risk_bundle = bundle["risk_model"]
        risk_classifier = risk_bundle["estimator"]
        metadata = risk_bundle["metadata"]
        probabilities = risk_classifier.predict_proba(frame)[0]
        labels = risk_classifier.classes_
        risk_lookup = {"LOW": 0.15, "ELEVATED": 0.58, "HIGH": 0.88}
        model_risk = float(sum(probabilities[index] * risk_lookup[label] for index, label in enumerate(labels)))
        transparent_risk, _ = _fallback(payload)
        shortage_risk = max(model_risk, transparent_risk)
        risk_level = _risk_level_from_score(shortage_risk)
        confidence = float(np.max(probabilities))
        top_factors = _top_factors(payload, metadata.get("top_features", []))
        model_source = str(metadata.get("selected_model", "Trained local classifier"))
        provenance = trained_ml_provenance(
            metadata,
            "Risk is produced by a locally trained inventory classifier and constrained by a transparent monotonic guard so what-if controls remain operationally coherent.",
        )
    else:
        shortage_risk, risk_level = _fallback(payload)
        confidence = 0.62
        top_factors = _top_factors(payload, ["shortage_score", "trolley_availability", "turnaround_pressure"])
        model_source = "Deterministic fallback"
        provenance = rule_based_provenance(
            "Fallback inventory scoring is active because the trained model artifact is unavailable. Risk is computed from transparent local rules."
        )

    trolley_status = (
        "Unavailable"
        if payload.trolley_availability < 0.35
        else "Constrained"
        if payload.trolley_availability < 0.62
        else "Available"
    )

    explanation_reasons = [factor.rstrip(".") for factor in top_factors[:2]]
    if len(explanation_reasons) > 1:
        explanation = (
            f"Inventory alert assessment indicates {explanation_reasons[0].lower()} "
            f"and {explanation_reasons[1].lower()}."
        )
    else:
        explanation = f"Inventory alert assessment indicates {explanation_reasons[0].lower()}."

    return InventoryPrediction(
        shortage_risk=round(shortage_risk, 3),
        risk_level=risk_level,
        affected_service_area=affected_area.replace("_", " "),
        confidence=round(confidence, 3),
        trolley_status=trolley_status,
        top_factors=top_factors,
        recommendation=_recommendation(risk_level, affected_area, payload.trolley_availability),
        explanation=explanation,
        model_source=model_source,
        provenance=provenance,
    )
