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
from app.training.generate_bottleneck_data import save_bottleneck_dataset


FEATURE_COLUMNS = [
    "passenger_load",
    "arrival_delay",
    "gate_congestion",
    "malfunction_count",
    "malfunction_severity",
    "inventory_shortage",
    "aircraft_type",
    "route_class",
    "assistance_request",
    "refueling_required",
    "weather_disturbance",
]

DOMAIN_TOP_FEATURES = [
    "inventory_shortage",
    "malfunction_severity",
    "weather_disturbance",
    "gate_congestion",
    "passenger_load",
    "arrival_delay",
    "malfunction_count",
    "refueling_required",
]


def _label(candidate_name: str) -> str:
    return candidate_name.replace("_", " ").title()


def train_and_save_bottleneck_model(
    output_path: Path | None = None,
    data_path: Path | None = None,
    force_data: bool = False,
    write_publication_artifacts: bool = True,
) -> Path:
    settings = get_settings()
    source = data_path or settings.data_dir / "bottleneck_training.csv"
    target = output_path or settings.model_dir / "bottleneck_bundle.joblib"

    if force_data or not source.exists():
        save_bottleneck_dataset(source, samples=5000, seed=settings.random_seed + 5)

    df = pd.read_csv(source)
    dev_df, test_df = fixed_dev_test_split(
        df,
        target_col="dominant_bottleneck",
        seed=settings.random_seed + 5,
        stratify=True,
    )

    categorical = ["aircraft_type", "route_class", "assistance_request", "refueling_required"]
    numeric = [column for column in FEATURE_COLUMNS if column not in categorical]

    candidates = {
        "logistic_regression": {
            "pipeline": Pipeline(
                steps=[
                    ("preprocessor", build_preprocessor(categorical, numeric, scale_numeric=True)),
                    (
                        "model",
                        LogisticRegression(
                            max_iter=1400,
                            class_weight="balanced",
                            random_state=settings.random_seed + 5,
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
                            n_estimators=240,
                            class_weight="balanced",
                            random_state=settings.random_seed + 6,
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
                    ("model", GradientBoostingClassifier(random_state=settings.random_seed + 7)),
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
    y_dev = dev_df["dominant_bottleneck"]
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df["dominant_bottleneck"]

    best_name, best_estimator, search_results = run_model_search(
        candidates=candidates,
        X_dev=X_dev,
        y_dev=y_dev,
        scoring="f1_macro",
        cv=classifier_cv(settings.random_seed + 5),
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
        feature_importance = compute_feature_importance(best_estimator, X_test, y_test, scoring="f1_macro")
        top_features = feature_importance["feature"].head(8).tolist()

        save_table(settings.table_dir / "bottleneck_model_comparison.csv", comparison_table)
        save_table(settings.table_dir / "bottleneck_feature_importance.csv", feature_importance)
        save_json(settings.table_dir / "bottleneck_holdout_metrics.json", metrics)

        plot_model_comparison(
            comparison_table,
            "development_cv_f1_macro",
            "Bottleneck Model Comparison (Development CV)",
            settings.figure_dir / "bottleneck_model_comparison.png",
        )
        labels, matrix = label_confusion(y_test, y_pred)
        plot_confusion(
            labels,
            matrix,
            "Bottleneck Holdout Confusion Matrix",
            settings.figure_dir / "bottleneck_confusion_matrix.png",
        )
        plot_feature_importance(
            feature_importance,
            "Bottleneck Top Feature Importance",
            settings.figure_dir / "bottleneck_feature_importance.png",
        )

    metadata = {
        "task": "turnaround_bottleneck_classification",
        "target": "dominant_bottleneck",
        "selected_model": _label(best_name),
        "development_metric_name": "macro F1",
        "development_metric_value": round(float(search_results[best_name]["best_score"]), 4),
        "test_metrics": {key: round(float(value), 4) for key, value in metrics.items()},
        "top_features": top_features,
        "split_policy": "Fixed 80% development / 20% holdout test; CV and tuning restricted to development split.",
        "synthetic_data_note": "Labels are created from process-aware sub-process duration simulations rather than direct class lookup formulas.",
        "limitations": "Probability quality is still bounded by synthetic scenario assumptions and should be treated as decision-support only.",
        "provenance_category": "trained_ml_inference",
        "sample_count": int(len(df)),
        "class_distribution": df["dominant_bottleneck"].value_counts(normalize=True).round(4).to_dict(),
    }

    joblib.dump(
        {
            "classifier": {
                "estimator": best_estimator,
                "metadata": metadata,
            },
            "feature_columns": FEATURE_COLUMNS,
        },
        target,
    )
    return target


if __name__ == "__main__":
    path = train_and_save_bottleneck_model(force_data=True)
    print(f"Saved bottleneck model to {path}")
