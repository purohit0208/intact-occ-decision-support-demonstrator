# JATM Scenario-Evaluation Artifacts

This folder contains the Journal of Air Transport Management revision artifacts for the OCC decision-support demonstrator.

## Contents

- `scripts/`: deterministic scenario-sweep, monotonicity, ablation, baseline, and manuscript-build scripts.
- `outputs/tables/`: generated CSV inputs, outputs, summaries, monotonicity results, ablations, and baselines.
- `outputs/figures/`: generated manuscript figures.
- `manuscript/`: revised manuscript source and Word files prepared from the generated artifacts.

## Reproducibility

From the repository root, run the scripts with the same Python environment used for the demonstrator backend:

```powershell
python paper_revision_jatm/scripts/run_scenario_sweep.py
python paper_revision_jatm/scripts/run_monotonicity_checks.py
python paper_revision_jatm/scripts/run_ablation_baseline.py
python paper_revision_jatm/scripts/build_jatm_manuscript.py
```

The scenario sweep uses deterministic seeds and evaluates synthetic inbound cases through the demonstrator's existing local model and fusion services.

## Evidence Boundary

These artifacts support controlled synthetic scenario evaluation only. They do not contain airline operational data and do not establish airline deployment, certification, OCC user validation, safety assurance, measured operational savings, or return on investment.
