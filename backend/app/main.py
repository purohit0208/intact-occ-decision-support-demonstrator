from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_bottleneck import router as bottleneck_router
from app.api.routes_demo import router as demo_router
from app.api.routes_fusion import router as fusion_router
from app.api.routes_health import router as health_router
from app.api.routes_inventory import router as inventory_router
from app.api.routes_maintenance import router as maintenance_router
from app.core.config import get_settings
from app.training.train_all import ensure_all_artifacts


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        ensure_all_artifacts(force_data=False)
    except Exception:
        pass
    yield


settings = get_settings()
app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    description="Local OCC decision-support research demonstrator for aircraft turnaround coordination.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(demo_router)
app.include_router(maintenance_router)
app.include_router(inventory_router)
app.include_router(bottleneck_router)
app.include_router(fusion_router)
