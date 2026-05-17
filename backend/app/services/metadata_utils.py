from __future__ import annotations

from app.schemas.common import ProvenanceInfo


PRIMARY_METRIC_KEYS = {
    "ROC-AUC": "roc_auc",
    "macro F1": "f1_macro",
    "RMSE": "rmse",
}


def metric_string(metric_name: str | None, value: float | None) -> str | None:
    if metric_name is None or value is None:
        return None
    return f"{metric_name}: {value:.3f}"


def trained_ml_provenance(metadata: dict, summary: str) -> ProvenanceInfo:
    metric_name = metadata.get("development_metric_name")
    test_metrics = metadata.get("test_metrics", {})
    primary_key = PRIMARY_METRIC_KEYS.get(metric_name or "", "")
    test_value = test_metrics.get(primary_key)

    return ProvenanceInfo(
        category="trained_ml_inference",
        label="Trained ML inference",
        summary=summary,
        selected_model=metadata.get("selected_model"),
        development_metric=metric_string(metric_name, metadata.get("development_metric_value")),
        test_metric=metric_string(metric_name, test_value),
    )


def rule_based_provenance(summary: str) -> ProvenanceInfo:
    return ProvenanceInfo(
        category="rule_based_logic",
        label="Rule-based logic",
        summary=summary,
    )


def scenario_provenance(summary: str) -> ProvenanceInfo:
    return ProvenanceInfo(
        category="scenario_simulation",
        label="Scenario simulation",
        summary=summary,
    )
