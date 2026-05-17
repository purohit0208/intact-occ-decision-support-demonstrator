from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from app.core.config import get_settings


AIRCRAFT_TYPES = ["A320neo", "A321", "B737-800", "E195-E2"]
ROUTE_CLASSES = ["short_haul", "medium_haul", "long_haul"]
BOTTLENECKS = ["Maintenance", "Catering", "Cleaning", "Boarding", "Refueling"]


def generate_bottleneck_dataset(samples: int = 900, seed: int | None = None) -> pd.DataFrame:
    rng = np.random.default_rng(seed or get_settings().random_seed)

    passenger_load = rng.integers(70, 220, size=samples)
    arrival_delay = rng.integers(0, 85, size=samples)
    gate_congestion = rng.uniform(0.5, 9.5, size=samples)
    malfunction_count = rng.poisson(1.4, size=samples).clip(0, 7)
    malfunction_severity = (rng.normal(2.7, 1.8, size=samples) + malfunction_count * 0.7).clip(0, 9.8)
    inventory_shortage = rng.uniform(0, 9.6, size=samples)
    aircraft_type = rng.choice(AIRCRAFT_TYPES, size=samples)
    route_class = rng.choice(ROUTE_CLASSES, size=samples, p=[0.45, 0.35, 0.2])
    assistance_request = rng.binomial(1, 0.22, size=samples).astype(bool)
    refueling_required = rng.binomial(1, 0.8, size=samples).astype(bool)
    weather_disturbance = rng.uniform(0, 8, size=samples)
    stand_pressure = gate_congestion * 0.55 + arrival_delay / 85 * 1.8 + rng.normal(0, 0.35, size=samples)
    route_turn_penalty = np.where(route_class == "long_haul", 2.8, np.where(route_class == "medium_haul", 1.1, 0))
    aircraft_penalty = np.where(aircraft_type == "A321", 0.8, np.where(aircraft_type == "B737-800", 0.4, 0))

    maintenance_duration = (
        5.8
        + malfunction_count * 1.7
        + malfunction_severity * 2.4
        + weather_disturbance * 0.45
        + stand_pressure * 0.35
        + rng.normal(0, 1.3, size=samples)
    )
    catering_duration = (
        7.7
        + inventory_shortage * 1.45
        + passenger_load / 220 * 6.5
        + route_turn_penalty * 0.65
        + stand_pressure * 0.4
        + rng.normal(0, 1.25, size=samples)
    )
    cleaning_duration = (
        9.7
        + passenger_load / 220 * 9.6
        + arrival_delay / 85 * 4.8
        + route_turn_penalty * 0.55
        + stand_pressure * 0.46
        + rng.normal(0, 1.45, size=samples)
    )
    boarding_duration = (
        9.8
        + passenger_load / 220 * 7.3
        + gate_congestion * 0.72
        + arrival_delay / 85 * 3.8
        + assistance_request.astype(int) * 1.9
        + route_turn_penalty * 0.35
        + rng.normal(0, 1.2, size=samples)
    )
    refueling_duration = (
        7.9
        + refueling_required.astype(int) * 5.7
        + arrival_delay / 85 * 4.0
        + weather_disturbance * 0.95
        + gate_congestion * 0.38
        + aircraft_penalty
        + rng.normal(0, 1.45, size=samples)
    )

    durations = np.column_stack(
        [maintenance_duration, catering_duration, cleaning_duration, boarding_duration, refueling_duration]
    )
    dominant_bottleneck = np.array(BOTTLENECKS)[durations.argmax(axis=1)]

    return pd.DataFrame(
        {
            "passenger_load": passenger_load,
            "arrival_delay": arrival_delay,
            "gate_congestion": gate_congestion.round(2),
            "malfunction_count": malfunction_count,
            "malfunction_severity": malfunction_severity.round(2),
            "inventory_shortage": inventory_shortage.round(2),
            "aircraft_type": aircraft_type,
            "route_class": route_class,
            "assistance_request": assistance_request,
            "refueling_required": refueling_required,
            "weather_disturbance": weather_disturbance.round(2),
            "maintenance_duration_proxy": maintenance_duration.round(2),
            "catering_duration_proxy": catering_duration.round(2),
            "cleaning_duration_proxy": cleaning_duration.round(2),
            "boarding_duration_proxy": boarding_duration.round(2),
            "refueling_duration_proxy": refueling_duration.round(2),
            "dominant_bottleneck": dominant_bottleneck,
        }
    )


def save_bottleneck_dataset(output_path: Path | None = None, samples: int = 900, seed: int | None = None) -> Path:
    settings = get_settings()
    path = output_path or settings.data_dir / "bottleneck_training.csv"
    df = generate_bottleneck_dataset(samples=samples, seed=seed)
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    path = save_bottleneck_dataset()
    print(f"Saved bottleneck dataset to {path}")
