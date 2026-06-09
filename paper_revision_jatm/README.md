# OCC Demonstrator JATM Revision Package

This folder contains the separate Journal of Air Transport Management revision package for the OCC decision-support manuscript.

The existing live OCC demo is treated as frozen. The scripts in this folder import existing backend service functions but do not edit backend, frontend, launcher, seeded-scenario, saved-model, or existing paper-package files.

## Main Commands

From the repository root, using the same Python environment as the demonstrator backend:

```powershell
python paper_revision_jatm\scripts\snapshot_frozen_demo.py --write-baseline
python paper_revision_jatm\scripts\run_scenario_sweep.py --scenarios 1000
python paper_revision_jatm\scripts\run_monotonicity_checks.py
python paper_revision_jatm\scripts\run_ablation_baseline.py
python paper_revision_jatm\scripts\build_jatm_manuscript.py
python paper_revision_jatm\scripts\snapshot_frozen_demo.py --compare
```

## Outputs

- `outputs\tables`: scenario sweep, regime, monotonicity, ablation, and baseline CSV files.
- `outputs\figures`: manuscript-scale evaluation figures.
- `manuscript`: revised JATM manuscript, title page, highlights, and submission notes.
- `reports`: technical change report, response-to-rejection note, go/no-go recommendation, and evaluation summaries.
- `snapshot`: frozen-demo manifest and comparison results.

## Claim Boundary

The generated evaluation package supports a controlled, reproducible scenario-based analysis of the implemented decision-support architecture. It does not establish real airline performance, OCC user acceptance, operational savings, certification readiness, or production deployment validity.
