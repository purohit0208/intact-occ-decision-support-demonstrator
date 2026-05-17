from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(__file__).resolve().parents[3] / "paper_assets" / "mplconfig" / f"pid_{os.getpid()}"),
)
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, KFold, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


matplotlib.use("Agg")
matplotlib.set_loglevel("error")


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def save_table(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def fixed_dev_test_split(
    frame: pd.DataFrame,
    target_col: str,
    seed: int,
    stratify: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    stratify_values = frame[target_col] if stratify else None
    dev_df, test_df = train_test_split(
        frame,
        test_size=0.2,
        random_state=seed,
        stratify=stratify_values,
    )
    return dev_df.reset_index(drop=True), test_df.reset_index(drop=True)


def build_preprocessor(
    categorical: list[str],
    numeric: list[str],
    scale_numeric: bool = False,
) -> ColumnTransformer:
    numeric_steps: list[tuple[str, Any]] = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))

    return ColumnTransformer(
        transformers=[
            ("num", Pipeline(steps=numeric_steps), numeric),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categorical,
            ),
        ]
    )


def classification_cv(results: dict[str, dict[str, Any]], metric_key: str) -> pd.DataFrame:
    return (
        pd.DataFrame(
            [
                {
                    "candidate": name,
                    "best_params": json.dumps(meta["best_params"], sort_keys=True),
                    metric_key: meta["best_score"],
                }
                for name, meta in results.items()
            ]
        )
        .sort_values(metric_key, ascending=False)
        .reset_index(drop=True)
    )


def regression_cv(results: dict[str, dict[str, Any]], metric_key: str) -> pd.DataFrame:
    return (
        pd.DataFrame(
            [
                {
                    "candidate": name,
                    "best_params": json.dumps(meta["best_params"], sort_keys=True),
                    metric_key: meta["best_score"],
                }
                for name, meta in results.items()
            ]
        )
        .sort_values(metric_key, ascending=True)
        .reset_index(drop=True)
    )


def run_model_search(
    *,
    candidates: dict[str, dict[str, Any]],
    X_dev: pd.DataFrame,
    y_dev: pd.Series,
    scoring: str,
    cv,
    higher_is_better: bool,
) -> tuple[str, Any, dict[str, dict[str, Any]]]:
    search_results: dict[str, dict[str, Any]] = {}
    best_name = ""
    best_estimator = None
    best_score = -np.inf if higher_is_better else np.inf

    for name, spec in candidates.items():
        search = GridSearchCV(
            estimator=spec["pipeline"],
            param_grid=spec["param_grid"],
            scoring=scoring,
            cv=cv,
            n_jobs=1,
            refit=True,
        )
        search.fit(X_dev, y_dev)
        score = float(search.best_score_)
        search_results[name] = {
            "best_params": search.best_params_,
            "best_score": score,
            "estimator": search.best_estimator_,
        }

        if higher_is_better and score > best_score:
            best_score = score
            best_name = name
            best_estimator = search.best_estimator_
        if not higher_is_better and score < best_score:
            best_score = score
            best_name = name
            best_estimator = search.best_estimator_

    if best_estimator is None:
        raise RuntimeError("Model search did not produce a fitted estimator.")

    return best_name, best_estimator, search_results


def binary_classification_metrics(
    y_true: pd.Series,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None = None,
) -> dict[str, float]:
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }
    if y_proba is not None:
        metrics["roc_auc"] = float(roc_auc_score(y_true, y_proba))
    return metrics


def multiclass_classification_metrics(
    y_true: pd.Series,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None = None,
) -> dict[str, float]:
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }
    if y_proba is not None:
        labels = sorted(pd.Series(y_true).unique().tolist())
        metrics["roc_auc_ovr"] = float(roc_auc_score(y_true, y_proba, multi_class="ovr", labels=labels))
        metrics["brier_score"] = float(multiclass_brier_score(y_true, y_proba, labels))
    return metrics


def multiclass_brier_score(y_true: pd.Series, y_proba: np.ndarray, labels: list[Any]) -> float:
    encoded = pd.get_dummies(pd.Categorical(y_true, categories=labels)).to_numpy()
    return float(np.mean(np.sum((y_proba - encoded) ** 2, axis=1)))


def regression_metrics(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": rmse,
        "r2": float(r2_score(y_true, y_pred)),
    }


def compute_feature_importance(
    estimator,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    scoring: str,
    repeats: int = 8,
) -> pd.DataFrame:
    importance = permutation_importance(
        estimator,
        X_test,
        y_test,
        scoring=scoring,
        n_repeats=repeats,
        random_state=42,
        n_jobs=1,
    )
    frame = pd.DataFrame(
        {
            "feature": list(X_test.columns),
            "importance_mean": importance.importances_mean,
            "importance_std": importance.importances_std,
        }
    ).sort_values("importance_mean", ascending=False)
    return frame.reset_index(drop=True)


def plot_model_comparison(frame: pd.DataFrame, metric_col: str, title: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(frame["candidate"], frame[metric_col], color="#54d1db")
    ax.set_title(title)
    ax.set_xlabel(metric_col.replace("_", " ").title())
    ax.invert_yaxis()
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_confusion(labels: list[str], matrix: np.ndarray, title: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    image = ax.imshow(matrix, cmap="Blues")
    ax.set_title(title)
    ax.set_xticks(range(len(labels)), labels=labels, rotation=30, ha="right")
    ax.set_yticks(range(len(labels)), labels=labels)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            ax.text(col, row, int(matrix[row, col]), ha="center", va="center", color="#0f172a")
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_feature_importance(frame: pd.DataFrame, title: str, output_path: Path, top_n: int = 10) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    trimmed = frame.head(top_n).sort_values("importance_mean", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.barh(trimmed["feature"], trimmed["importance_mean"], color="#f59e0b")
    ax.set_title(title)
    ax.set_xlabel("Permutation importance")
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_regression_scatter(y_true: pd.Series, y_pred: np.ndarray, title: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    ax.scatter(y_true, y_pred, alpha=0.55, color="#54d1db", edgecolor="none")
    lower = float(min(np.min(y_true), np.min(y_pred)))
    upper = float(max(np.max(y_true), np.max(y_pred)))
    ax.plot([lower, upper], [lower, upper], linestyle="--", color="#f97316", linewidth=1.5)
    ax.set_title(title)
    ax.set_xlabel("Actual")
    ax.set_ylabel("Predicted")
    ax.grid(linestyle="--", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def classifier_cv(seed: int) -> StratifiedKFold:
    return StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)


def regressor_cv(seed: int) -> KFold:
    return KFold(n_splits=5, shuffle=True, random_state=seed)


def label_confusion(y_true: pd.Series, y_pred: np.ndarray) -> tuple[list[str], np.ndarray]:
    labels = sorted(pd.concat([pd.Series(y_true), pd.Series(y_pred)]).drop_duplicates().tolist())
    return labels, confusion_matrix(y_true, y_pred, labels=labels)
