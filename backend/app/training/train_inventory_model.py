from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.core.config import get_settings
from app.training.evaluation_utils import (
    build_preprocessor,
    classification_cv,
    classifier_cv,
    compute_feature_importance,
    fixed_dev_test_split,
    label_confusion,
    multiclass_classification_metrics,
    plot_confusion,
    plot_feature_importance,
    plot_model_comparison,
    run_model_search,
    save_json,
    save_table,
)
from app.training.generate_inventory_data import save_inventory_dataset


FEATURE_COLUMNS = [
    "route_class",
    "passenger_load",
    "service_profile",
    "shortage_score",
    "trolley_availability",
    "catering_complexity",
    "turnaround_pressure",
    "item_criticality",
    "inventory_category",
]

DOMAIN_TOP_FEATURES = [
    "trolley_availability",
    "shortage_score",
    "turnaround_pressure",
    "catering_complexity",
    "item_criticality",
    "passenger_load",
    "inventory_category",
    "service_profile",
]


def _label(candidate_name: str) -> str:
    return candidate_name.replace("_", " ").title()


def train_and_save_inventory_model(
    output_path: Path | None = None,
    data_path: Path | None = None,
    force_data: bool = False,
    write_publication_artifacts: bool = True,
) -> Path:
    settings = get_settings()
    source = data_path or settings.data_dir / "inventory_training.csv"
    target = output_path or settings.model_dir / "inventory_bundle.joblib"

    if force_data or not source.exists():
        save_inventory_dataset(source, samples=5000, seed=settings.random_seed + 3)

    df = pd.read_csv(source)
    dev_df, test_df = fixed_dev_test_split(df, target_col="risk_level", seed=settings.random_seed + 3, stratify=True)

    categorical = ["route_class", "service_profile", "inventory_category"]
    numeric = [column for column in FEATURE_COLUMNS if column not in categorical]

    candidates = {
        "logistic_regression": {
            "pipeline": Pipeline(
                steps=[
                    ("preprocessor", build_preprocessor(categorical, numeric, scale_numeric=True)),
                    (
                        "model",
                        LogisticRegression(
                            max_iter=1200,
                            class_weight="balanced",
                            random_state=settings.random_seed + 3,
                        ),
                    ),
                ]
            ),
            "param_grid": {"model__C": [0.35, 1.0, 3.5]},
        },
        "random_forest": {
            "pipeline": Pipeline(
                steps=[
                    ("preprocessor", build_preprocessor(categorical, numeric)),
                    (
                        "model",
                        RandomForestClassifier(
                            n_estimators=220,
                            class_weight="balanced",
                            random_state=settings.random_seed + 4,
                        ),
                    ),
                ]
            ),
            "param_grid": {"model__max_depth": [None, 10, 16], "model__min_samples_leaf": [1, 2, 4]},
        },
        "gradient_boosting": {
            "pipeline": Pipeline(
                steps=[
                    ("preprocessor", build_preprocessor(categorical, numeric)),
                    ("model", GradientBoostingClassifier(random_state=settings.random_seed + 5)),
                ]
            ),
            "param_grid": {
                "model__learning_rate": [0.05, 0.1],
                "model__max_depth": [2, 3],
                "model__n_estimators": [140, 220],
            },
        },
    }

    X_dev = dev_df[FEATURE_COLUMNS]
    y_dev = dev_df["risk_level"]
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df["risk_level"]

    best_name, best_estimator, search_results = run_model_search(
        candidates=candidates,
        X_dev=X_dev,
        y_dev=y_dev,
        scoring="f1_macro",
        cv=classifier_cv(settings.random_seed + 3),
        higher_is_better=True,
    )

    best_estimator.fit(X_dev, y_dev)
    y_pred = best_estimator.predict(X_test)
    y_proba = best_estimator.predict_proba(X_test)
    metrics = multiclass_classification_metrics(y_test, y_pred, y_proba)
    feature_importance = None
    top_features = DOMAIN_TOP_FEATURES

    comparison_table = classification_cv(search_results, "development_cv_f1_macro")
    if write_publication_artifacts:
        feature_importance = compute_feature_importance(
            best_estimator,
            X_test,
            y_test,
            scoring="f1_macro",
        )
        top_features = feature_importance["feature"].head(8).tolist()

        save_table(settings.table_dir / "inventory_risk_model_comparison.csv", comparison_table)
        save_table(settings.table_dir / "inventory_risk_feature_importance.csv", feature_importance)
        save_json(settings.table_dir / "inventory_risk_holdout_metrics.json", metrics)

        plot_model_comparison(
            comparison_table,
            "development_cv_f1_macro",
            "Inventory Risk Model Comparison (Development CV)",
            settings.figure_dir / "inventory_risk_model_comparison.png",
        )
        labels, matrix = label_confusion(y_test, y_pred)
        plot_confusion(
            labels,
            matrix,
            "Inventory Risk Holdout Confusion Matrix",
            settings.figure_dir / "inventory_risk_confusion_matrix.png",
        )
        plot_feature_importance(
            feature_importance,
            "Inventory Risk Top Feature Importance",
            settings.figure_dir / "inventory_risk_feature_importance.png",
        )

    metadata = {
        "task": "inventory_risk_level_classification",
        "target": "risk_level",
        "selected_model": _label(best_name),
        "development_metric_name": "macro F1",
        "development_metric_value": round(float(search_results[best_name]["best_score"]), 4),
        "test_metrics": {key: round(float(value), 4) for key, value in metrics.items()},
        "top_features": top_features,
        "split_policy": "Fixed 80% development / 20% holdout test; CV and tuning restricted to development split.",
        "synthetic_data_note": "Risk labels are generated from latent demand-supply mismatch, hidden loading error, and turnaround pressure. shortage_score is a noisy proxy, not the target itself.",
        "limitations": "Model outputs remain limited by synthetic data assumptions and should not be claimed as airline-validated performance.",
        "provenance_category": "trained_ml_inference",
        "sample_count": int(len(df)),
        "class_distribution": df["risk_level"].value_counts(normalize=True).round(4).to_dict(),
    }

    joblib.dump(
        {
            "risk_model": {
                "estimator": best_estimator,
                "metadata": metadata,
            },
            "feature_columns": FEATURE_COLUMNS,
        },
        target,
    )
    return target


if __name__ == "__main__":
    path = train_and_save_inventory_model(force_data=True)
    print(f"Saved inventory model to {path}")
