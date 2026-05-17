from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings


def train_all_artifacts(force_data: bool = False) -> list[Path]:
    from app.training.generate_publication_assets import generate_publication_assets
    from app.training.train_bottleneck_model import train_and_save_bottleneck_model
    from app.training.train_inventory_model import train_and_save_inventory_model
    from app.training.train_maintenance_model import train_and_save_maintenance_model

    artifacts = [
        train_and_save_maintenance_model(force_data=force_data),
        train_and_save_inventory_model(force_data=force_data),
        train_and_save_bottleneck_model(force_data=force_data),
    ]
    artifacts.extend(generate_publication_assets())
    return artifacts


def required_artifacts() -> list[Path]:
    settings = get_settings()
    return [
        settings.model_dir / "maintenance_bundle.joblib",
        settings.model_dir / "inventory_bundle.joblib",
        settings.model_dir / "bottleneck_bundle.joblib",
        settings.figure_dir / "system_architecture_publication.png",
        settings.table_dir / "module_evaluation_summary.csv",
        settings.table_dir / "panel_truthfulness_map.csv",
        settings.report_dir / "artifact_index.md",
    ]


def ensure_all_artifacts(force_data: bool = False) -> list[Path]:
    required = required_artifacts()
    if force_data or any(not path.exists() for path in required):
        return train_all_artifacts(force_data=force_data)
    return required


if __name__ == "__main__":
    for artifact in train_all_artifacts(force_data=True):
        print(f"Saved artifact: {artifact}")
