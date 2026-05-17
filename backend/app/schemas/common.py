from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


ProvenanceCategory = Literal[
    "trained_ml_inference",
    "rule_based_logic",
    "scenario_simulation",
    "fallback_placeholder",
]


class ProvenanceInfo(BaseModel):
    category: ProvenanceCategory
    label: str
    summary: str
    selected_model: str | None = None
    development_metric: str | None = None
    test_metric: str | None = None
