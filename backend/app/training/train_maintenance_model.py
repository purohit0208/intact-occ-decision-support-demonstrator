from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline

from app.core.config import get_settings
from app.training.evaluation_utils import (
    binary_classification_metrics,
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
    plot_regression_scatter,
    regressor_cv,
    regression_metrics,
    run_model_search,
    save_json,
    save_table,
)
from app.training.generate_maintenance_data import save_maintenance_dataset


FEATURE_COLUMNS = [
    "aircraft_type",
    "component_type",
    "aircraft_age_cycles",
    "flight_duration_hr",
    "cabin_temperature",
    "humidity",
    "passenger_load",
    "cycles_since_install",
    "wear_index",
    "malfunction_count",
    "malfunction_severity",
    "environmental_stress",
]


def _label(candidate_name: str) -> str:
    return candidate_name.replace("_", " ").title()


SPLIT_POLICY = "Fixed 80% development / 20% holdout test; CV and tuning restricted to development split."
SYNTHETIC_NOTE = (
    "Maintenance targets are generated from a Weibull-inspired hazard proxy, incident pressure, and environmental "
    "acceleration."
)
LIMITATIONS_NOTE = (
    "Outputs remain tied to synthetic but operationally grounded data and should not be claimed as certified "
    "maintenance planning performance."
)


def train_and_save_maintenance_model(
    output_path: Path | None = None,
    data_path: Path | None = None,
    force_data: bool = False,
) -> Path:
    settings = get_settings()
    source = data_path or settings.data_dir / "maintenance_training.csv"
    target = output_path or settings.model_dir / "maintenance_bundle.joblib"

    if force_data or not source.exists():
        save_maintenance_dataset(source, samples=5000, seed=settings.random_seed)

    df = pd.read_csv(source)
    dev_df, test_df = fixed_dev_test_split(
        df,
        target_col="failure_next_n_flights",
        seed=settings.random_seed,
        stratify=True,
    )

    categorical = ["aircraft_type", "component_type"]
    numeric = [column for column in FEATURE_COLUMNS if column not in categorical]

    X_dev = dev_df[FEATURE_COLUMNS]
    X_test = test_df[FEATURE_COLUMNS]

    failure_candidates = {
        "logistic_regression": {
            "pipeline": Pipeline(
                steps=[
                    ("preprocessor", build_preprocessor(categorical, numeric, scale_numeric=True)),
                    (
                        "model",
                        LogisticRegression(max_iter=1200, class_weight="balanced", random_state=settings.random_seed),
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
                            random_state=settings.random_seed + 1,
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
                    ("model", GradientBoostingClassifier(random_state=settings.random_seed + 2)),
                ]
            ),
            "param_grid": {
                "model__learning_rate": [0.05, 0.1],
                "model__max_depth": [2, 3],
                "model__n_estimators": [140, 220],
            },
        },
    }

    best_failure_name, best_failure_estimator, failure_search = run_model_search(
        candidates=failure_candidates,
        X_dev=X_dev,
        y_dev=dev_df["failure_next_n_flights"],
        scoring="roc_auc",
        cv=classifier_cv(settings.random_seed),
        higher_is_better=True,
    )
    best_failure_estimator.fit(X_dev, dev_df["failure_next_n_flights"])
    failure_pred = best_failure_estimator.predict(X_test)
    failure_proba = best_failure_estimator.predict_proba(X_test)[:, 1]
    failure_metrics = binary_classification_metrics(test_df["failure_next_n_flights"], failure_pred, failure_proba)
    failure_importance = compute_feature_importance(
        best_failure_estimator,
        X_test,
        test_df["failure_next_n_flights"],
        scoring="roc_auc",
    )

    failure_table = classification_cv(failure_search, "development_cv_roc_auc")
    save_table(settings.table_dir / "maintenance_failure_model_comparison.csv", failure_table)
    save_table(settings.table_dir / "maintenance_failure_feature_importance.csv", failure_importance)
    save_json(settings.table_dir / "maintenance_failure_holdout_metrics.json", failure_metrics)
    plot_model_comparison(
        failure_table,
        "development_cv_roc_auc",
        "Maintenance Failure Model Comparison (Development CV)",
        settings.figure_dir / "maintenance_failure_model_comparison.png",
    )
    labels, matrix = label_confusion(test_df["failure_next_n_flights"], failure_pred)
    plot_confusion(
        labels,
        matrix,
        "Maintenance Failure Holdout Confusion Matrix",
        settings.figure_dir / "maintenance_failure_confusion_matrix.png",
    )
    plot_feature_importance(
        failure_importance,
        "Maintenance Failure Top Feature Importance",
        settings.figure_dir / "maintenance_failure_feature_importance.png",
    )

    urgency_candidates = {
        "logistic_regression": {
            "pipeline": Pipeline(
                steps=[
                    ("preprocessor", build_preprocessor(categorical, numeric, scale_numeric=True)),
                    (
                        "model",
                        LogisticRegression(
                            max_iter=1400,
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

    best_urgency_name, best_urgency_estimator, urgency_search = run_model_search(
        candidates=urgency_candidates,
        X_dev=X_dev,
        y_dev=dev_df["urgency_class"],
        scoring="f1_macro",
        cv=classifier_cv(settings.random_seed + 1),
        higher_is_better=True,
    )
    best_urgency_estimator.fit(X_dev, dev_df["urgency_class"])
    urgency_pred = best_urgency_estimator.predict(X_test)
    urgency_proba = best_urgency_estimator.predict_proba(X_test)
    urgency_metrics = multiclass_classification_metrics(test_df["urgency_class"], urgency_pred, urgency_proba)
    urgency_importance = compute_feature_importance(
        best_urgency_estimator,
        X_test,
        test_df["urgency_class"],
        scoring="f1_macro",
    )

    urgency_table = classification_cv(urgency_search, "development_cv_f1_macro")
    save_table(settings.table_dir / "maintenance_urgency_model_comparison.csv", urgency_table)
    save_table(settings.table_dir / "maintenance_urgency_feature_importance.csv", urgency_importance)
    save_json(settings.table_dir / "maintenance_urgency_holdout_metrics.json", urgency_metrics)
    plot_model_comparison(
        urgency_table,
        "development_cv_f1_macro",
        "Maintenance Urgency Model Comparison (Development CV)",
        settings.figure_dir / "maintenance_urgency_model_comparison.png",
    )
    urgency_labels, urgency_matrix = label_confusion(test_df["urgency_class"], urgency_pred)
    plot_confusion(
        urgency_labels,
        urgency_matrix,
        "Maintenance Urgency Holdout Confusion Matrix",
        settings.figure_dir / "maintenance_urgency_confusion_matrix.png",
    )
    plot_feature_importance(
        urgency_importance,
        "Maintenance Urgency Top Feature Importance",
        settings.figure_dir / "maintenance_urgency_feature_importance.png",
    )

    rul_candidates = {
        "ridge_regression": {
            "pipeline": Pipeline(
                steps=[
                    ("preprocessor", build_preprocessor(categorical, numeric, scale_numeric=True)),
                    ("model", Ridge(random_state=settings.random_seed + 6)),
                ]
            ),
            "param_grid": {"model__alpha": [0.5, 1.0, 3.0]},
        },
        "random_forest_regressor": {
            "pipeline": Pipeline(
                steps=[
                    ("preprocessor", build_preprocessor(categorical, numeric)),
                    ("model", RandomForestRegressor(n_estimators=220, random_state=settings.random_seed + 7)),
                ]
            ),
            "param_grid": {"model__max_depth": [None, 10, 16], "model__min_samples_leaf": [1, 2, 4]},
        },
        "gradient_boosting_regressor": {
            "pipeline": Pipeline(
                steps=[
                    ("preprocessor", build_preprocessor(categorical, numeric)),
                    ("model", GradientBoostingRegressor(random_state=settings.random_seed + 8)),
                ]
            ),
            "param_grid": {
                "model__learning_rate": [0.05, 0.1],
                "model__max_depth": [2, 3],
                "model__n_estimators": [140, 220],
            },
        },
    }

    best_rul_name, best_rul_estimator, rul_search = run_model_search(
        candidates=rul_candidates,
        X_dev=X_dev,
        y_dev=dev_df["remaining_flights_estimate"],
        scoring="neg_root_mean_squared_error",
        cv=regressor_cv(settings.random_seed + 2),
        higher_is_better=True,
    )
    best_rul_estimator.fit(X_dev, dev_df["remaining_flights_estimate"])
    rul_pred = best_rul_estimator.predict(X_test)
    rul_metrics = regression_metrics(test_df["remaining_flights_estimate"], rul_pred)
    rul_importance = compute_feature_importance(
        best_rul_estimator,
        X_test,
        test_df["remaining_flights_estimate"],
        scoring="neg_root_mean_squared_error",
    )

    rul_table = pd.DataFrame(
        [
            {
                "candidate": name,
                "best_params": search["best_params"],
                "development_cv_rmse": round(-float(search["best_score"]), 4),
            }
            for name, search in rul_search.items()
        ]
    ).sort_values("development_cv_rmse", ascending=True)
    save_table(settings.table_dir / "maintenance_rul_model_comparison.csv", rul_table)
    save_table(settings.table_dir / "maintenance_rul_feature_importance.csv", rul_importance)
    save_json(settings.table_dir / "maintenance_rul_holdout_metrics.json", rul_metrics)
    plot_model_comparison(
        rul_table,
        "development_cv_rmse",
        "Maintenance RUL Model Comparison (Lower Is Better)",
        settings.figure_dir / "maintenance_rul_model_comparison.png",
    )
    plot_regression_scatter(
        test_df["remaining_flights_estimate"],
        rul_pred,
        "Maintenance RUL Holdout Predictions",
        settings.figure_dir / "maintenance_rul_scatter.png",
    )
    plot_feature_importance(
        rul_importance,
        "Maintenance RUL Top Feature Importance",
        settings.figure_dir / "maintenance_rul_feature_importance.png",
    )

    joblib.dump(
        {
            "failure_model": {
                "estimator": best_failure_estimator,
                "metadata": {
                    "task": "maintenance_failure_probability",
                    "target": "failure_next_n_flights",
                    "selected_model": _label(best_failure_name),
                    "development_metric_name": "ROC-AUC",
                    "development_metric_value": round(float(failure_search[best_failure_name]["best_score"]), 4),
                    "test_metrics": {key: round(float(value), 4) for key, value in failure_metrics.items()},
                    "top_features": failure_importance["feature"].head(8).tolist(),
                    "split_policy": SPLIT_POLICY,
                    "synthetic_data_note": SYNTHETIC_NOTE,
                    "limitations": LIMITATIONS_NOTE,
                    "provenance_category": "trained_ml_inference",
                },
            },
            "urgency_model": {
                "estimator": best_urgency_estimator,
                "metadata": {
                    "task": "maintenance_urgency_classification",
                    "target": "urgency_class",
                    "selected_model": _label(best_urgency_name),
                    "development_metric_name": "macro F1",
                    "development_metric_value": round(float(urgency_search[best_urgency_name]["best_score"]), 4),
                    "test_metrics": {key: round(float(value), 4) for key, value in urgency_metrics.items()},
                    "top_features": urgency_importance["feature"].head(8).tolist(),
                    "split_policy": SPLIT_POLICY,
                    "synthetic_data_note": SYNTHETIC_NOTE,
                    "limitations": LIMITATIONS_NOTE,
                    "provenance_category": "trained_ml_inference",
                },
            },
            "rul_model": {
                "estimator": best_rul_estimator,
                "metadata": {
                    "task": "maintenance_remaining_flights_regression",
                    "target": "remaining_flights_estimate",
                    "selected_model": _label(best_rul_name),
                    "development_metric_name": "RMSE",
                    "development_metric_value": round(-float(rul_search[best_rul_name]["best_score"]), 4),
                    "test_metrics": {key: round(float(value), 4) for key, value in rul_metrics.items()},
                    "top_features": rul_importance["feature"].head(8).tolist(),
                    "split_policy": SPLIT_POLICY,
                    "synthetic_data_note": SYNTHETIC_NOTE,
                    "limitations": LIMITATIONS_NOTE,
                    "provenance_category": "trained_ml_inference",
                },
            },
            "feature_columns": FEATURE_COLUMNS,
            "split_policy": SPLIT_POLICY,
            "synthetic_data_note": SYNTHETIC_NOTE,
            "limitations": LIMITATIONS_NOTE,
            "provenance_category": "trained_ml_inference",
        },
        target,
    )
    return target


if __name__ == "__main__":
    path = train_and_save_maintenance_model(force_data=True)
    print(f"Saved maintenance model to {path}")
