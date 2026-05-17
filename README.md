# INTACT OCC Decision Support Demonstrator

Local hybrid OCC decision-support research demonstrator for aircraft turnaround operations in the INTACT project context.

In this public repository, `<repo-root>` means the local folder where this repository has been cloned or extracted.

This repository is intentionally framed as:

- a research demonstrator
- a decision-support prototype
- a synthetic but operationally grounded local simulation
- a human-in-the-loop OCC interface

This repository is not framed as:

- production airline software
- an autonomous operations platform
- a cloud service
- a validated live airline deployment

## Project Purpose

The demonstrator shows how aircraft-side structured information can be transmitted before landing, processed by local predictive modules, and fused into an OCC dashboard to support turnaround coordination.

The integrated scope covers four research streams:

- passenger assistance readiness
- inventory and trolley visibility
- predictive maintenance for in-cabin components
- turnaround bottleneck prediction

For publication-oriented use, the repository also exports local evaluation tables, provenance maps, and paper-ready figures under `<repo-root>\paper_assets`.

## Quick Start

If the dependencies are already installed on the laptop, the simplest way to run the demonstrator is:

1. Download or clone this repository on a Windows laptop.
2. Double-click `Start-OCC-Demo.bat` from the repository root.
3. Wait for the browser to open.
4. Present the app at `http://127.0.0.1:5173`.

When the demonstration is finished, double-click `Stop-OCC-Demo.bat`.

## Architecture Summary

The local system is organized into four layers:

1. Input / scenario layer
   Aircraft-side and operational context inputs such as flight details, delay, congestion, passenger assistance, inventory signals, and malfunction indicators.
2. Analytics / inference layer
   Separate local predictive modules for maintenance, inventory intelligence, and bottleneck prediction.
3. OCC fusion / decision-support layer
   Transparent rule-based readiness scoring, alert prioritization, operator advisories, and action queue generation.
4. Presentation layer
   A local web GUI with dashboard, flight detail, scenario lab, impact framing, and architecture explanation.

## Folder Structure

```text
intact-occ-decision-support-demonstrator
+-- backend
|   +-- app
|       +-- api
|       +-- core
|       +-- data
|       +-- models
|       +-- schemas
|       +-- services
|       +-- training
+-- frontend
|   +-- src
|   |   +-- components
|   |   +-- data
|   |   +-- lib
|   |   +-- pages
|   |   +-- styles
|   |   +-- types
|   +-- package.json
+-- Start-OCC-Demo.bat
+-- Stop-OCC-Demo.bat
+-- Run-OCC-Backend.bat
+-- Run-OCC-Frontend.bat
+-- OCC-Demo.docx
+-- README.md
+-- requirements.txt
```

## Backend Setup On Windows

Requirements:

- Python 3.11 or newer

Open PowerShell in `<repo-root>` and run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m ensurepip --upgrade
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Frontend Setup On Windows

Requirements:

- Node.js 20 or newer
- npm

Open a second PowerShell window in `<repo-root>\frontend` and run:

```powershell
npm install
```

## Very Short Run Guide

If you prefer commands instead of the batch launcher:

1. Backend window:

```powershell
cd <repo-root>\backend
<repo-root>\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

2. Frontend window:

```powershell
cd <repo-root>\frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

3. Open:

```text
http://127.0.0.1:5173
```

## Optional Docker Run

Docker is optional. The primary supported path for the demonstrator remains the local Windows run flow above.

If Docker Desktop is installed, you can also run:

```powershell
cd <repo-root>
docker compose up --build
```

Then open:

```text
http://127.0.0.1:5173
```

This Docker path is intended for portability and reproducibility when handing the demonstrator to other researchers.

## Run The Backend

From `<repo-root>`:

```powershell
cd backend
<repo-root>\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Backend endpoints:

- `GET /health`
- `GET /demo/flights`
- `GET /demo/scenarios`
- `GET /demo/flights/{flight_id}`
- `POST /predict/maintenance`
- `POST /predict/inventory`
- `POST /predict/bottleneck`
- `POST /predict/fusion`
- `POST /scenario/recompute`

The backend loads saved local model bundles from `<repo-root>\backend\app\models`. If a required model bundle is missing, the corresponding service attempts local retraining for that module.

If model loading or local retraining cannot complete, the API still starts and falls back to deterministic local scoring logic where implemented.

## Run The Frontend

From `<repo-root>\frontend`:

```powershell
npm run dev -- --host 127.0.0.1 --port 5173
```

Default frontend URL:

- `http://127.0.0.1:5173`

The Vite dev server proxies local API requests to `http://127.0.0.1:8000`.

## Train Models Explicitly

If you want to regenerate all synthetic data and demo models manually:

```powershell
cd <repo-root>\backend
<repo-root>\.venv\Scripts\python.exe -m app.training.train_all
```

Individual training scripts are also available:

- `<repo-root>\.venv\Scripts\python.exe -m app.training.train_maintenance_model`
- `<repo-root>\.venv\Scripts\python.exe -m app.training.train_inventory_model`
- `<repo-root>\.venv\Scripts\python.exe -m app.training.train_bottleneck_model`

To regenerate the publication-oriented figures, tables, and artifact index without retraining the models:

- `<repo-root>\.venv\Scripts\python.exe -m app.training.generate_publication_assets`

## Run Backend Tests

From `<repo-root>\backend`:

```powershell
<repo-root>\.venv\Scripts\python.exe -m pytest tests
```

Synthetic data generation scripts:

- `<repo-root>\.venv\Scripts\python.exe -m app.training.generate_maintenance_data`
- `<repo-root>\.venv\Scripts\python.exe -m app.training.generate_inventory_data`
- `<repo-root>\.venv\Scripts\python.exe -m app.training.generate_bottleneck_data`

Generated files are written to:

- `<repo-root>\backend\app\data`
- `<repo-root>\backend\app\models`
- `<repo-root>\paper_assets\figures`
- `<repo-root>\paper_assets\tables`
- `<repo-root>\paper_assets\reports`

## Paper-Ready Artifacts

The paper-supporting artifacts currently generated by the repository include:

- model comparison figures
- confusion matrices
- feature-importance plots
- a publication-oriented architecture figure
- module evaluation summary tables
- a panel truthfulness map
- reproducibility notes
- a structured demonstrator audit report

Key files:

- `<repo-root>\paper_assets\reports\demonstrator_audit_report.md`
- `<repo-root>\paper_assets\reports\reproducibility_notes.md`
- `<repo-root>\paper_assets\reports\artifact_index.md`

## Frontend Pages

### Dashboard

Shows all inbound demo flights with fused summary state:

- readiness score
- dominant bottleneck
- maintenance urgency
- inventory alert status
- passenger assistance status
- fused alert level

### Flight Detail

Shows one selected flight in depth:

- aircraft-side / cabin report panel
- predictive maintenance panel
- inventory intelligence panel
- passenger assistance panel
- bottleneck distribution panel
- recommended OCC actions panel

### Scenario Lab

Supports what-if exploration by changing:

- passenger load
- arrival delay
- malfunction count
- malfunction severity
- inventory shortage
- gate congestion
- trolley availability
- passenger assistance state
- weather disturbance

Every change triggers local recomputation of:

- maintenance outputs
- inventory outputs
- bottleneck probabilities
- readiness score
- action queue
- estimated impact indicators

### Impact Page

Shows:

- simulated proactive vs reactive framing
- expected delay-risk indication
- readiness and response improvement indicators
- project-level INTACT reference metrics clearly separated from software outputs

### Architecture / About

Explains:

- aircraft-side reporting layer
- module-level predictive analytics
- OCC fusion logic
- human-in-the-loop positioning
- conservative academic framing

## Default Demo Cases

The seeded demo flights include:

1. A maintenance-driven critical case
2. An inventory / trolley issue case
3. A passenger assistance readiness case
4. A normal low-risk case
5. A composite multi-risk case

## Troubleshooting

### Backend import errors

If `fastapi`, `pydantic`, `pandas`, `scikit-learn`, or `joblib` are missing, reinstall the backend dependencies:

```powershell
<repo-root>\.venv\Scripts\python.exe -m pip install -r <repo-root>\requirements.txt
```

### Frontend command not found

If `npm` is not available, install Node.js 20+ and reopen PowerShell.

### One-click launcher

If you want the simplest presentation flow, use `Start-OCC-Demo.bat` instead of launching the backend and frontend manually.

### Models missing

No manual repair should be required. Start the backend again and it will attempt local model training automatically. If this fails, deterministic fallback scoring is used.

### Scenario lab fallback mode

If the backend is not running, the scenario lab displays a limited frontend fallback response so the page still renders. Start the backend to enable the full local inference and fusion pipeline.

## Research Framing Notes

Use terms such as:

- decision support
- predicted risk
- estimated impact
- simulated scenario
- operator advisory
- readiness

Avoid interpreting the demonstrator as:

- autonomous control
- guaranteed savings
- production-certified software
- a live airline-validated deployment

