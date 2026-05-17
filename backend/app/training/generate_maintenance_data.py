from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from app.core.config import get_settings


AIRCRAFT_TYPES = ["A320neo", "A321", "B737-800", "E195-E2"]
COMPONENT_TYPES = [
    "seat_power_unit",
    "galley_chiller",
    "ife_display",
    "lavatory_sensor",
    "cabin_light_driver",
]

COMPONENT_ETA = {
    "seat_power_unit": 3100,
    "galley_chiller": 2200,
    "ife_display": 2600,
    "lavatory_sensor": 2800,
    "cabin_light_driver": 3400,
}

COMPONENT_BETA = {
    "seat_power_unit": 2.3,
    "galley_chiller": 2.8,
    "ife_display": 2.4,
    "lavatory_sensor": 2.1,
    "cabin_light_driver": 2.0,
}


def generate_maintenance_dataset(samples: int = 700, seed: int | None = None) -> pd.DataFrame:
    rng = np.random.default_rng(seed or get_settings().random_seed)

    aircraft_type = rng.choice(AIRCRAFT_TYPES, size=samples, p=[0.35, 0.2, 0.3, 0.15])
    component_type = rng.choice(COMPONENT_TYPES, size=samples)
    passenger_load = rng.integers(70, 215, size=samples)
    aircraft_age_cycles = rng.integers(2800, 31000, size=samples)
    flight_duration_hr = rng.uniform(0.9, 5.5, size=samples)
    cabin_temperature = rng.normal(23.0, 4.0, size=samples).clip(16, 35)
    humidity = rng.normal(38.0, 11.0, size=samples).clip(12, 78)
    cycles_since_install = rng.integers(60, 4100, size=samples)
    wear_index = rng.normal(48, 18, size=samples).clip(5, 97)
    malfunction_count = rng.poisson(1.8, size=samples).clip(0, 7)
    malfunction_severity = (
        rng.normal(3.2, 1.8, size=samples)
        + malfunction_count * 0.55
        + np.where(component_type == "galley_chiller", 0.6, 0)
    ).clip(0, 9.8)
    environmental_stress = (
        (humidity - 20) / 15
        + np.maximum(cabin_temperature - 24, 0) / 2.7
        + rng.normal(0.2, 0.9, size=samples)
    ).clip(0, 10)

    eta = np.array([COMPONENT_ETA[item] for item in component_type], dtype=float)
    beta = np.array([COMPONENT_BETA[item] for item in component_type], dtype=float)

    environmental_acceleration = (
        1
        + np.maximum(cabin_temperature - 24, 0) * 0.018
        + np.maximum(humidity - 45, 0) * 0.006
        + environmental_stress * 0.045
    )
    wear_pressure = 0.32 + wear_index / 100 * 0.9
    usage_fraction = np.clip(cycles_since_install / eta, 0.05, 2.4)
    weibull_hazard = 1 - np.exp(-((usage_fraction**beta) * environmental_acceleration * wear_pressure))

    incident_pressure = (
        malfunction_severity / 10 * 0.34
        + malfunction_count / 7 * 0.16
        + passenger_load / 220 * 0.08
        + aircraft_age_cycles / 31000 * 0.06
    )
    risk_score = np.clip(0.02 + weibull_hazard * 0.62 + incident_pressure + rng.normal(0, 0.035, size=samples), 0.01, 0.99)

    failure_next_n_flights = rng.binomial(1, risk_score)
    remaining_flights_estimate = np.round(
        62
        - risk_score * 50
        - usage_fraction * 11
        - malfunction_severity * 1.2
        + rng.normal(0, 3.5, size=samples)
    ).clip(0, 65)

    urgency_class = np.select(
        [
            (risk_score >= 0.78) | (remaining_flights_estimate <= 5),
            (risk_score >= 0.58) | (remaining_flights_estimate <= 12),
            (risk_score >= 0.36) | (remaining_flights_estimate <= 24),
        ],
        ["CRITICAL", "SOON", "PLAN"],
        default="OK",
    )

    return pd.DataFrame(
        {
            "aircraft_type": aircraft_type,
            "component_type": component_type,
            "aircraft_age_cycles": aircraft_age_cycles,
            "flight_duration_hr": flight_duration_hr.round(2),
            "cabin_temperature": cabin_temperature.round(2),
            "humidity": humidity.round(2),
            "passenger_load": passenger_load,
            "cycles_since_install": cycles_since_install,
            "wear_index": wear_index.round(2),
            "malfunction_count": malfunction_count,
            "malfunction_severity": malfunction_severity.round(2),
            "environmental_stress": environmental_stress.round(2),
            "weibull_hazard_proxy": weibull_hazard.round(4),
            "failure_next_n_flights": failure_next_n_flights.astype(int),
            "remaining_flights_estimate": remaining_flights_estimate.astype(int),
            "urgency_class": urgency_class,
        }
    )


def save_maintenance_dataset(output_path: Path | None = None, samples: int = 700, seed: int | None = None) -> Path:
    settings = get_settings()
    path = output_path or settings.data_dir / "maintenance_training.csv"
    df = generate_maintenance_dataset(samples=samples, seed=seed)
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    path = save_maintenance_dataset()
    print(f"Saved maintenance dataset to {path}")
