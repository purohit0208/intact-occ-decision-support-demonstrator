from __future__ import annotations

import csv
import json
import os
import textwrap
from pathlib import Path

import joblib

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(__file__).resolve().parents[3] / "paper_assets" / "mplconfig" / "publication_assets"),
)
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from app.core.config import get_settings


matplotlib.use("Agg")
matplotlib.set_loglevel("error")


TRUTHFULNESS_ROWS = [
    {
        "page": "Dashboard",
        "panel": "Inbound flight summary cards",
        "classification": "Rule-based logic",
        "note": "Cards aggregate rule-based fusion outputs computed over the current synthetic inbound scenario set.",
    },
    {
        "page": "Dashboard",
        "panel": "Inbound flight list / fused summary row",
        "classification": "Rule-based logic",
        "note": "Each row summarizes scenario state plus module outputs using deterministic OCC fusion and summary assembly logic.",
    },
    {
        "page": "Flight detail",
        "panel": "Aircraft-side / cabin report",
        "classification": "Scenario simulation",
        "note": "Pre-arrival cabin, assistance, and trolley signals are synthetic but operationally grounded scenario inputs.",
    },
    {
        "page": "Flight detail",
        "panel": "Predictive maintenance intelligence",
        "classification": "Trained ML inference",
        "note": "Failure probability, urgency class, and remaining-flights proxy are produced by locally trained models on synthetic reliability-oriented data.",
    },
    {
        "page": "Flight detail",
        "panel": "Inventory intelligence",
        "classification": "Trained ML inference",
        "note": "Inventory risk combines a locally trained classifier with a transparent monotonic what-if guard; affected area and recommendation are transparent post-model operational logic.",
    },
    {
        "page": "Flight detail",
        "panel": "Passenger assistance readiness",
        "classification": "Rule-based logic",
        "note": "Assistance readiness is intentionally implemented as dispatch-support logic rather than unsupported localization ML.",
    },
    {
        "page": "Flight detail",
        "panel": "Turnaround bottleneck prediction",
        "classification": "Trained ML inference",
        "note": "Dominant bottleneck and probability distribution are produced by a local multiclass model trained on process-aware synthetic turnaround data.",
    },
    {
        "page": "Flight detail",
        "panel": "Readiness score and action queue",
        "classification": "Rule-based logic",
        "note": "Fusion outputs are deterministic OCC coordination logic built on module outputs and scenario state.",
    },
    {
        "page": "Scenario lab",
        "panel": "Scenario recomputation output",
        "classification": "Scenario simulation",
        "note": "Operator input changes deterministically recompute the synthetic scenario state before module inference and fusion are re-run locally.",
    },
    {
        "page": "Impact",
        "panel": "Proactive versus reactive comparison widget",
        "classification": "Scenario simulation",
        "note": "Delay-risk and benefit indicators are demonstrator-level simulated impact values, not validated airline deployment outcomes.",
    },
    {
        "page": "Architecture",
        "panel": "Truthfulness and limitations disclosure",
        "classification": "Rule-based logic",
        "note": "This page is explanatory metadata documenting provenance, reproducibility, and limitations rather than a predictive module.",
    },
    {
        "page": "Offline fallback mode",
        "panel": "Frontend fallback responses when backend is unavailable",
        "classification": "Placeholder or fake intelligence",
        "note": "These responses are deliberate resilience placeholders only and should not be used as evidence of model behavior.",
    },
]


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _maintenance_rows(bundle: dict) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    specs = [
        ("Predictive maintenance", "failure_model", "maintenance_failure_holdout_metrics.json"),
        ("Predictive maintenance", "urgency_model", "maintenance_urgency_holdout_metrics.json"),
        ("Predictive maintenance", "rul_model", "maintenance_rul_holdout_metrics.json"),
    ]
    for module_name, key, metric_file in specs:
        metadata = bundle[key]["metadata"]
        test_metrics = _read_json(get_settings().table_dir / metric_file)
        rows.append(
            {
                "module": module_name,
                "task": metadata.get("task", key),
                "target": metadata.get("target", ""),
                "provenance": "Trained ML inference",
                "selected_model": metadata.get("selected_model", ""),
                "development_metric_name": metadata.get("development_metric_name", ""),
                "development_metric_value": str(metadata.get("development_metric_value", "")),
                "holdout_metrics": json.dumps(test_metrics, sort_keys=True),
                "top_features": "; ".join(metadata.get("top_features", [])[:5]),
                "split_policy": metadata.get("split_policy", bundle.get("split_policy", "")),
                "limitations": metadata.get("limitations", bundle.get("limitations", "")),
            }
        )
    return rows


def _inventory_rows(bundle: dict) -> list[dict[str, str]]:
    metadata = bundle["risk_model"]["metadata"]
    return [
        {
            "module": "Inventory intelligence",
            "task": metadata.get("task", "inventory"),
            "target": metadata.get("target", ""),
            "provenance": "Trained ML inference",
            "selected_model": metadata.get("selected_model", ""),
            "development_metric_name": metadata.get("development_metric_name", ""),
            "development_metric_value": str(metadata.get("development_metric_value", "")),
            "holdout_metrics": json.dumps(_read_json(get_settings().table_dir / "inventory_risk_holdout_metrics.json"), sort_keys=True),
            "top_features": "; ".join(metadata.get("top_features", [])[:5]),
            "split_policy": metadata.get("split_policy", ""),
            "limitations": metadata.get("limitations", ""),
        }
    ]


def _bottleneck_rows(bundle: dict) -> list[dict[str, str]]:
    metadata = bundle["classifier"]["metadata"]
    return [
        {
            "module": "Bottleneck prediction",
            "task": metadata.get("task", "bottleneck"),
            "target": metadata.get("target", ""),
            "provenance": "Trained ML inference",
            "selected_model": metadata.get("selected_model", ""),
            "development_metric_name": metadata.get("development_metric_name", ""),
            "development_metric_value": str(metadata.get("development_metric_value", "")),
            "holdout_metrics": json.dumps(_read_json(get_settings().table_dir / "bottleneck_holdout_metrics.json"), sort_keys=True),
            "top_features": "; ".join(metadata.get("top_features", [])[:5]),
            "split_policy": metadata.get("split_policy", ""),
            "limitations": metadata.get("limitations", ""),
        }
    ]


def _save_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _wrap_for_box(text: str, width: float, *, scale: float = 105.0) -> str:
    max_chars = max(18, int(width * scale))
    wrapped_lines: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            wrapped_lines.append("")
            continue
        wrapped_lines.extend(textwrap.wrap(line, width=max_chars, break_long_words=False, break_on_hyphens=False))
    return "\n".join(wrapped_lines)


def _draw_box(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    body: str,
    facecolor: str,
    *,
    title_fontsize: float = 13,
    body_fontsize: float = 9.5,
    title_spacing: float = 0.045,
) -> None:
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        linewidth=1.2,
        edgecolor="#1f3145",
        facecolor=facecolor,
    )
    ax.add_patch(patch)
    title_text = _wrap_for_box(title, w, scale=70.0)
    body_text = _wrap_for_box(body, w, scale=92.0)
    title_lines = title_text.count("\n") + 1
    title_artist = ax.text(
        x + (w / 2),
        y + h - 0.035,
        title_text,
        fontsize=title_fontsize,
        fontweight="bold",
        color="#f8fafc",
        va="top",
        ha="center",
        multialignment="center",
    )
    title_artist.set_clip_path(patch)
    title_artist.set_clip_on(True)

    body_top = y + h - (title_spacing + (title_lines * 0.042))
    body_artist = ax.text(
        x + (w / 2),
        body_top,
        body_text,
        fontsize=body_fontsize,
        color="#dbe4ee",
        va="top",
        ha="center",
        multialignment="center",
        linespacing=1.28,
    )
    body_artist.set_clip_path(patch)
    body_artist.set_clip_on(True)


def _draw_arrow(ax, start: tuple[float, float], end: tuple[float, float], rad: float = 0.0) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=1.5,
            color="#54d1db",
            alpha=0.9,
            zorder=10,
        )
    )

def _generate_architecture_figure(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(14, 8.8))
    fig.patch.set_facecolor("#07111d")
    ax.set_facecolor("#07111d")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.03,
        0.965,
        "INTACT OCC Research Demonstrator Architecture",
        fontsize=18,
        fontweight="bold",
        color="#f8fafc",
        va="top",
    )
    ax.text(
        0.03,
        0.93,
        "Local, human-in-the-loop, synthetic but operationally grounded decision-support architecture.",
        fontsize=10.5,
        color="#cbd5e1",
        va="top",
    )

    _draw_box(
        ax,
        0.03,
        0.48,
        0.28,
        0.30,
        "Aircraft-side information layer",
        "Structured cabin malfunction reporting\nPassenger assistance requests\nTrolley and inventory visibility\nTurnaround context inputs",
        "#102235",
        title_fontsize=13,
        body_fontsize=9,
    )
    _draw_box(
        ax,
        0.38,
        0.66,
        0.26,
        0.20,
        "Predictive maintenance module",
        "Trained local ML\nFailure probability, urgency, remaining-flights proxy",
        "#113347",
        title_fontsize=12,
        body_fontsize=7.8,
    )
    _draw_box(
        ax,
        0.38,
        0.40,
        0.26,
        0.20,
        "Inventory intelligence module",
        "Trained local ML\nShortage risk, confidence, affected service area",
        "#113347",
        title_fontsize=12,
        body_fontsize=7.8,
        title_spacing=0.035,
    )
    _draw_box(
        ax,
        0.70,
        0.40,
        0.26,
        0.20,
        "Assistance readiness support",
        "Rule-based support\nDispatch readiness, equipment confirmation",
        "#24324a",
        title_fontsize=12,
        body_fontsize=7.8,
    )
    _draw_box(
        ax,
        0.70,
        0.66,
        0.26,
        0.20,
        "Bottleneck prediction module",
        "Trained local ML\nClass probabilities across turnaround bottlenecks",
        "#113347",
        title_fontsize=12,
        body_fontsize=7.8,
    )
    _draw_box(
        ax,
        0.24,
        0.20,
        0.52,
        0.14,
        "OCC fusion layer",
        "Rule-based readiness scoring, escalation,\naction queue, and what-if comparison",
        "#1d3243",
        title_fontsize=12.5,
        body_fontsize=8.5,
    )
    _draw_box(
        ax,
        0.14,
        0.03,
        0.72,
        0.12,
        "Operator-facing interface",
        "Dashboard, flight detail, scenario lab,\nimpact/KPI and architecture views",
        "#102235",
        title_fontsize=12.5,
        body_fontsize=8.5,
    )

    # Arrows from Aircraft-side
    _draw_arrow(ax, (0.31, 0.72), (0.38, 0.72))
    _draw_arrow(ax, (0.31, 0.76), (0.70, 0.78))
    _draw_arrow(ax, (0.31, 0.50), (0.38, 0.50))
    _draw_arrow(ax, (0.31, 0.59), (0.70, 0.59))

    # Arrows to OCC Fusion
    _draw_arrow(ax, (0.51, 0.40), (0.47, 0.34))
    _draw_arrow(ax, (0.83, 0.40), (0.58, 0.34))
    _draw_arrow(ax, (0.64, 0.66), (0.64, 0.34))
    _draw_arrow(ax, (0.70, 0.66), (0.68, 0.34))

    # Arrow from Fusion to Interface
    _draw_arrow(ax, (0.50, 0.20), (0.50, 0.15))

    ax.text(
        0.015,
        0.015,
        "Publication asset: architecture overview for paper or presentation use. Dashboard, flight detail, scenario lab, impact/KPI page, and architecture page with provenance badges and limitations disclosure.",
        fontsize=6,
        color="#5a6b7c",
        va="bottom",
    )

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def _artifact_rows(directory: Path, kind: str) -> list[dict[str, str]]:
    return [
        {
            "kind": kind,
            "filename": path.name,
            "path": str(path),
        }
        for path in sorted(directory.glob("*"))
        if path.is_file()
    ]


def generate_publication_assets() -> list[Path]:
    settings = get_settings()
    settings.figure_dir.mkdir(parents=True, exist_ok=True)
    settings.table_dir.mkdir(parents=True, exist_ok=True)
    settings.report_dir.mkdir(parents=True, exist_ok=True)

    maintenance_bundle = joblib.load(settings.model_dir / "maintenance_bundle.joblib")
    inventory_bundle = joblib.load(settings.model_dir / "inventory_bundle.joblib")
    bottleneck_bundle = joblib.load(settings.model_dir / "bottleneck_bundle.joblib")

    evaluation_rows = []
    evaluation_rows.extend(_maintenance_rows(maintenance_bundle))
    evaluation_rows.extend(_inventory_rows(inventory_bundle))
    evaluation_rows.extend(_bottleneck_rows(bottleneck_bundle))

    truthfulness_path = settings.table_dir / "panel_truthfulness_map.csv"
    evaluation_path = settings.table_dir / "module_evaluation_summary.csv"
    figures_manifest_path = settings.table_dir / "generated_figures.csv"
    tables_manifest_path = settings.table_dir / "generated_tables.csv"
    reports_manifest_path = settings.table_dir / "generated_reports.csv"
    architecture_path = settings.figure_dir / "system_architecture_publication.png"
    artifact_index_path = settings.report_dir / "artifact_index.md"

    _save_csv(truthfulness_path, TRUTHFULNESS_ROWS)
    _save_csv(evaluation_path, evaluation_rows)
    _generate_architecture_figure(architecture_path)
    _save_csv(figures_manifest_path, _artifact_rows(settings.figure_dir, "figure"))
    _save_csv(tables_manifest_path, _artifact_rows(settings.table_dir, "table"))
    _save_csv(reports_manifest_path, _artifact_rows(settings.report_dir, "report"))

    figures = sorted(path.name for path in settings.figure_dir.glob("*") if path.is_file())
    tables = sorted(path.name for path in settings.table_dir.glob("*") if path.is_file())
    reports = sorted(path.name for path in settings.report_dir.glob("*") if path.is_file())
    artifact_index_path.write_text(
        "\n".join(
            [
                "# Publication Artifact Index",
                "",
                "## Figures",
                *[f"- {name}" for name in figures],
                "",
                "## Tables",
                *[f"- {name}" for name in tables],
                "",
                "## Reports",
                *[f"- {name}" for name in reports],
                "",
                "## Notes",
                "- Figures and tables are generated locally from the saved model artifacts and evaluation outputs.",
                "- UI screenshots are intentionally excluded from automatic generation in this script; they should be captured manually from the running local demonstrator after the final visual review.",
            ]
        ),
        encoding="utf-8",
    )

    return [
        truthfulness_path,
        evaluation_path,
        figures_manifest_path,
        tables_manifest_path,
        reports_manifest_path,
        architecture_path,
        artifact_index_path,
    ]


if __name__ == "__main__":
    for artifact in generate_publication_assets():
        print(f"Generated publication artifact: {artifact}")
