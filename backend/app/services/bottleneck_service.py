from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from app.core.config import get_settings
from app.schemas.bottleneck import BottleneckDistribution, BottleneckInput, BottleneckPrediction
from app.services.metadata_utils import rule_based_provenance, trained_ml_provenance


BOTTLENECKS = ["Maintenance", "Catering", "Cleaning", "Boarding", "Refueling"]


def _bundle_path() -> Path:
    return get_settings().model_dir / "bottleneck_bundle.joblib"


@lru_cache(maxsize=1)
def _load_bundle() -> dict | None:
    path = _bundle_path()
    try:
        if not path.exists():
            from app.training.train_bottleneck_model import train_and_save_bottleneck_model

            train_and_save_bottleneck_model()
        return joblib.load(path)
    except Exception:
        return None


def _fallback_scores(payload: BottleneckInput) -> dict[str, float]:
    scores = {
        "Maintenance": payload.malfunction_count * 0.22 + payload.malfunction_severity * 0.55 + payload.gate_congestion * 0.08,
        "Catering": payload.inventory_shortage * 0.5 + payload.passenger_load / 220 * 2.1 + payload.gate_congestion * 0.16,
        "Cleaning": payload.passenger_load / 220 * 2.3 + payload.arrival_delay / 85 * 1.5 + payload.gate_congestion * 0.14,
        "Boarding": payload.passenger_load / 220 * 2.7 + payload.gate_congestion * 0.28 + payload.arrival_delay / 85 * 1.1 + (0.6 if payload.assistance_request else 0.0),
        "Refueling": (1.6 if payload.refueling_required else 0.6) + payload.arrival_delay / 85 * 1.0 + payload.weather_disturbance * 0.14,
    }
    total = sum(max(value, 0.001) for value in scores.values())
    return {key: value / total for key, value in scores.items()}


def _top_factors(payload: BottleneckInput, dominant: str) -> list[str]:
    factors: list[str] = []
    if dominant == "Maintenance":
        if payload.malfunction_severity >= 6:
            factors.append("high malfunction severity")
        if payload.malfunction_count >= 3:
            factors.append("multiple cabin discrepancies")
    if dominant == "Catering":
        if payload.inventory_shortage >= 6:
            factors.append("inventory shortage risk")
        if payload.passenger_load >= 170:
            factors.append("high service demand")
    if dominant == "Cleaning":
        if payload.arrival_delay >= 20:
            factors.append("compressed ground time")
        if payload.passenger_load >= 170:
            factors.append("higher cabin turnover")
    if dominant == "Boarding":
        if payload.gate_congestion >= 6:
            factors.append("elevated gate congestion")
        if payload.passenger_load >= 170:
            factors.append("boarding volume")
        if payload.assistance_request:
            factors.append("active assistance coordination")
    if dominant == "Refueling":
        if payload.refueling_required:
            factors.append("refueling requirement")
        if payload.weather_disturbance >= 4:
            factors.append("weather disturbance")
        if payload.arrival_delay >= 20:
            factors.append("arrival delay")
    if not factors:
        factors.append("mixed operational pressure")
    return factors[:3]


def _recommended_response(dominant: str) -> str:
    responses = {
        "Maintenance": "Prepare maintenance dispatch and protect the post-arrival inspection slot.",
        "Catering": "Protect the catering uplift sequence and confirm trolley readiness before stand arrival.",
        "Cleaning": "Pre-brief the cleaning team on compressed ground time and cabin turnover pressure.",
        "Boarding": "Coordinate early gate preparation and monitor passenger flow constraints.",
        "Refueling": "Confirm refueling slot availability and validate stand-side access timing.",
    }
    return responses[dominant]


def predict_bottleneck(payload: BottleneckInput) -> BottleneckPrediction:
    bundle = _load_bundle()
    if bundle:
        frame = pd.DataFrame([payload.model_dump()])
        classifier_bundle = bundle["classifier"]
        classifier = classifier_bundle["estimator"]
        metadata = classifier_bundle["metadata"]
        raw = classifier.predict_proba(frame)[0]
        distribution = {label: 0.0 for label in BOTTLENECKS}
        for index, label in enumerate(classifier.classes_):
            distribution[str(label)] = float(raw[index])
        model_source = str(metadata.get("selected_model", "Trained local bottleneck model"))
        provenance = trained_ml_provenance(
            metadata,
            "Bottleneck probabilities are produced by a locally trained multiclass classifier selected through development-set cross-validation on process-aware synthetic turnaround scenarios.",
        )
    else:
        distribution = _fallback_scores(payload)
        model_source = "Deterministic fallback"
        provenance = rule_based_provenance(
            "Fallback bottleneck scoring is active because the trained model artifact is unavailable. Probabilities are derived from transparent process heuristics."
        )

    dominant = max(distribution, key=distribution.get)
    top_factors = _top_factors(payload, dominant)
    explanation = f"{dominant} is currently the leading turnaround bottleneck based on {', '.join(top_factors[:2])}."
    confidence = float(distribution[dominant])

    return BottleneckPrediction(
        probabilities=BottleneckDistribution(**{key: round(distribution[key], 3) for key in BOTTLENECKS}),
        dominant_bottleneck=dominant,
        confidence=round(confidence, 3),
        top_contributing_factors=top_factors,
        explanation=explanation,
        recommended_response=_recommended_response(dominant),
        model_source=model_source,
        provenance=provenance,
    )
