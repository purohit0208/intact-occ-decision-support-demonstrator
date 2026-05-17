from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field


class Settings(BaseModel):
    project_name: str = "INTACT OCC Decision Support Demonstrator"
    api_prefix: str = ""
    repo_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[3])
    backend_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2])
    app_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1])
    model_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1] / "models")
    data_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1] / "data")
    paper_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[3] / "paper_assets")
    figure_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[3] / "paper_assets" / "figures")
    table_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[3] / "paper_assets" / "tables")
    report_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[3] / "paper_assets" / "reports")
    random_seed: int = 42
    frontend_origin: str = "http://localhost:5173"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.model_dir.mkdir(parents=True, exist_ok=True)
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.paper_dir.mkdir(parents=True, exist_ok=True)
    settings.figure_dir.mkdir(parents=True, exist_ok=True)
    settings.table_dir.mkdir(parents=True, exist_ok=True)
    settings.report_dir.mkdir(parents=True, exist_ok=True)
    return settings
