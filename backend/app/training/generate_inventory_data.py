from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from app.core.config import get_settings


ROUTE_CLASSES = ["short_haul", "medium_haul", "long_haul"]
SERVICE_PROFILES = ["standard", "business_priority", "high_turnover", "late_rotation"]
INVENTORY_CATEGORIES = ["beverage", "meal", "duty_free", "wheelchair_kit", "mixed_service"]


def generate_inventory_dataset(samples: int = 700, seed: int | None = None) -> pd.DataFrame:
    rng = np.random.default_rng(seed or get_settings().random_seed)

    route_class = rng.choice(ROUTE_CLASSES, size=samples, p=[0.45, 0.35, 0.2])
    passenger_load = rng.integers(70, 220, size=samples)
    service_profile = rng.choice(SERVICE_PROFILES, size=samples)
    shortage_score = rng.uniform(0.2, 9.8, size=samples)
    trolley_availability = rng.uniform(0.25, 1.0, size=samples)
    catering_complexity = rng.uniform(1, 9.5, size=samples)
    turnaround_pressure = rng.uniform(1, 9.5, size=samples)
    item_criticality = rng.uniform(1, 9.5, size=samples)
    inventory_category = rng.choice(INVENTORY_CATEGORIES, size=samples)
    hidden_demand_shock = rng.normal(0, 0.75, size=samples)
    hidden_loading_error = rng.normal(0, 0.7, size=samples)
    hidden_restock_delay = rng.beta(2.0, 3.5, size=samples)

    passenger_demand = passenger_load * np.where(service_profile == "business_priority", 1.12, 1.0)
    route_demand = np.select(
        [route_class == "long_haul", route_class == "medium_haul"],
        [13.0, 6.0],
        default=1.5,
    )
    category_bias = np.select(
        [
            inventory_category == "meal",
            inventory_category == "beverage",
            inventory_category == "duty_free",
            inventory_category == "wheelchair_kit",
        ],
        [12.0, 9.0, 5.0, 3.0],
        default=7.0,
    )

    latent_required_units = (
        passenger_demand * 0.085
        + route_demand
        + category_bias
        + catering_complexity * 1.05
        + item_criticality * 0.7
        + shortage_score * 0.55
        + hidden_demand_shock * 2.4
    )

    latent_available_units = (
        trolley_availability * 44
        + np.maximum(0, 11 - turnaround_pressure) * 1.2
        + np.where(service_profile == "late_rotation", -3.5, 0)
        + hidden_loading_error * 3.0
        - hidden_restock_delay * turnaround_pressure * 2.2
    )

    shortage_gap = np.maximum(latent_required_units - latent_available_units, 0)
    disruption_score = np.clip(
        0.13 * shortage_gap
        + (1 - trolley_availability) * 9
        + turnaround_pressure * 0.75
        + np.where(route_class == "long_haul", 1.5, 0)
        + hidden_restock_delay * 3.0
        + rng.normal(0, 1.8, size=samples),
        0,
        None,
    )

    risk_score = 1 / (1 + np.exp(-(disruption_score - 8.0) / 3.2))

    risk_level = np.select([risk_score >= 0.72, risk_score >= 0.43], ["HIGH", "ELEVATED"], default="LOW")

    affected_service_area = np.select(
        [
            inventory_category == "mixed_service",
            inventory_category == "meal",
            inventory_category == "beverage",
            inventory_category == "duty_free",
            inventory_category == "wheelchair_kit",
        ],
        [
            np.where(
                service_profile == "business_priority",
                "premium_cabin",
                np.where(route_class == "long_haul", "long_haul_service", "standard_service"),
            ),
            "meal",
            "beverage",
            "duty_free",
            "wheelchair_kit",
        ],
        default="standard_service",
    )

    action_class = np.select(
        [risk_score >= 0.76, risk_score >= 0.48],
        ["replace_trolley_set", "top_up_before_arrival"],
        default="monitor_only",
    )

    return pd.DataFrame(
        {
            "route_class": route_class,
            "passenger_load": passenger_load,
            "service_profile": service_profile,
            "shortage_score": shortage_score.round(2),
            "trolley_availability": trolley_availability.round(2),
            "catering_complexity": catering_complexity.round(2),
            "turnaround_pressure": turnaround_pressure.round(2),
            "item_criticality": item_criticality.round(2),
            "inventory_category": inventory_category,
            "latent_required_units": latent_required_units.round(2),
            "latent_available_units": latent_available_units.round(2),
            "shortage_gap": shortage_gap.round(2),
            "risk_level": risk_level,
            "affected_service_area": affected_service_area,
            "action_class": action_class,
        }
    )


def save_inventory_dataset(output_path: Path | None = None, samples: int = 700, seed: int | None = None) -> Path:
    settings = get_settings()
    path = output_path or settings.data_dir / "inventory_training.csv"
    df = generate_inventory_dataset(samples=samples, seed=seed)
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    path = save_inventory_dataset()
    print(f"Saved inventory dataset to {path}")
