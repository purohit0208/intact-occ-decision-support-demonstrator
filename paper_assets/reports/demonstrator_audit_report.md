# INTACT OCC Demonstrator Audit Report

## Audit Basis

This audit was conducted against the following repository and source materials:

- `D:\OCC-Demo\OCC-Demo.docx`
- `D:\OCC-Demo\INTACT_Paper_Final.pdf`
- `D:\OCC-Demo\Predictive Maintenance Framework.pdf`
- `D:\OCC-Demo\StudentProject_Shanthi.pdf`
- the full demonstrator codebase under `D:\OCC-Demo\backend` and `D:\OCC-Demo\frontend`
- generated model artifacts, evaluation tables, and figures under `D:\OCC-Demo\backend\app\models` and `D:\OCC-Demo\paper_assets`

The original demonstrator brief in `OCC-Demo.docx` defines the system as a local, human-in-the-loop OCC research demonstrator rather than production airline software. The existing inventory paper in `INTACT_Paper_Final.pdf` explicitly acknowledges reliance on synthetic data, a single 80/20 split, and the absence of cross-validation and a separate final holdout workflow. Those points were treated as central audit targets.

## A. Current Architecture Summary

### Frontend pages

The demonstrator currently exposes five primary pages plus a not-found route:

- `Dashboard`
- `Flight detail`
- `Scenario lab`
- `Impact`
- `Architecture`
- `Not found`

The dashboard presents inbound-flight summaries and fused alerts. The flight-detail page is the core demonstrator page and includes aircraft-side reporting, predictive maintenance, inventory intelligence, passenger assistance readiness, bottleneck prediction, and the action queue. The scenario lab supports what-if recomputation. The impact page shows simulated proactive-versus-reactive indicators and separates those from project-level INTACT reference metrics. The architecture page now exposes provenance, reproducibility, and limitation notes rather than acting only as a static overview.

### Backend structure

The backend is a local FastAPI application with routes for:

- `GET /health`
- `GET /demo/flights`
- `GET /demo/scenarios`
- `GET /demo/flights/{flight_id}`
- `POST /predict/maintenance`
- `POST /predict/inventory`
- `POST /predict/bottleneck`
- `POST /predict/fusion`
- `POST /scenario/recompute`

The main service layers are:

- scenario construction and seeded demo flights
- predictive maintenance inference
- inventory intelligence inference
- bottleneck prediction inference
- OCC fusion and action generation
- local training and publication-asset generation scripts

### Scenario logic

The scenario layer is implemented through a fixed set of seeded inbound cases and a recomputation path for operator-edited scenarios. The default cases now cover:

1. a maintenance-driven critical case
2. an inventory-driven service case
3. a passenger-assistance readiness case
4. a normal low-risk case
5. a composite multi-risk case

Scenario recomputation is deterministic. A change in scenario inputs triggers local recomputation of module inputs, module predictions, fusion outputs, and impact indicators.

### Prediction and intelligence panels

The current prediction-facing panels are:

- aircraft-side / cabin report
- predictive maintenance intelligence
- inventory intelligence
- passenger assistance readiness
- turnaround bottleneck prediction
- readiness score and action queue
- proactive-versus-reactive impact widget

Each major panel now exposes provenance metadata in the interface.

## B. Truthfulness Audit

### Classification by panel/output

The demonstrator now separates panel provenance into four categories:

- Trained ML inference
- Rule-based logic
- Scenario simulation
- Placeholder or fake intelligence

The detailed export is available at `D:\OCC-Demo\paper_assets\tables\panel_truthfulness_map.csv`.

#### Trained ML inference

- Predictive maintenance panel
- Inventory intelligence risk estimation
- Bottleneck prediction panel

These panels now use saved local model artifacts in `D:\OCC-Demo\backend\app\models`.

#### Rule-based logic

- Passenger assistance readiness panel
- Readiness score
- Alert prioritization
- Action queue
- Dashboard fused summary assembly
- Architecture-page provenance and limitations disclosure

This classification is appropriate because those outputs are intentionally implemented as transparent operational support logic rather than unsupported ML.

#### Scenario simulation

- Aircraft-side / cabin report panel
- Seeded inbound demo flights
- Scenario lab recomputation context
- Proactive-versus-reactive impact comparison
- Project-level impact framing derived from prior INTACT analysis

These outputs are scenario-driven or demonstrator-level simulation rather than validated operational measurements.

#### Placeholder or fake intelligence

- Frontend offline fallback responses when the backend is unavailable

These exist only to prevent blank-screen failures and are explicitly not evidence of model performance. The fallback mode must not be used in screenshots or paper figures that claim model behavior.

### Truthfulness finding

The demonstrator is now substantially more truthful than before the audit. The only remaining placeholder intelligence is the explicit frontend fallback mode. That mode is defensible as a resilience mechanism, but it must remain clearly excluded from evaluation claims.

## C. Scientific Risk Audit

### 1. Overclaim risk

The major historical overclaim risk was implicit: panels appeared predictive without consistently distinguishing trained inference from heuristics or scenario simulation. That risk has been reduced by:

- provenance badges in the UI
- a truthfulness mapping table
- explicit limitations text
- conservative wording in the architecture and impact pages

Residual overclaim risk remains if the paper describes the system as validated for airline operations. That would not be supportable.

### 2. Unsupported predictions

The assistance-related functionality does not have defensible evidence for a true localization model in this repository. It is therefore implemented as rule-based assistance-readiness support. This is the correct decision and should remain so in the paper.

The proactive-versus-reactive comparison remains simulated. It is suitable for architecture-level discussion but not for empirical operational-effect claims.

### 3. Validation gaps

The paper file `INTACT_Paper_Final.pdf` explicitly identifies the earlier methodological weakness: a single 80/20 split with no cross-validation and no separate final holdout workflow. The upgraded demonstrator now uses:

- a fixed 80% development split
- a fixed 20% final holdout test split
- cross-validation and hyperparameter tuning only inside the 80% development split

This resolves the prior workflow issue at demonstrator level. However, the remaining validation limits are still substantial:

- all evaluation is still on synthetic data
- there is no external airline dataset
- there is no temporal validation
- there is no domain-shift evaluation
- there is no calibration analysis beyond reporting Brier scores

### 4. Leakage risk

Leakage risk was highest in inventory intelligence because the earlier paper acknowledged simplified target construction and idealized synthetic structure. The upgraded inventory generator now derives risk from latent demand-supply mismatch, hidden loading error, and hidden restock delay; the observed shortage score is only a noisy proxy. This is a defensible improvement.

Residual leakage risk remains because the synthetic generator still defines the target process. A reviewer could still argue that the learning problem is easier than real operations. That criticism would be valid and should be acknowledged explicitly.

### 5. Reproducibility gaps

The demonstrator now has reproducible local scripts and exported artifacts, but several reproducibility limits remain:

- evaluation is seed-dependent synthetic-data generation
- no locked environment file beyond `requirements.txt`
- no formal experiment registry
- no automated UI screenshot pipeline

These are manageable for a capstone demonstrator paper if disclosed clearly.

### 6. Missing explanation or confidence outputs

This gap has been materially improved:

- trained panels now show provenance
- trained panels now expose confidence-style outputs
- top contributing factors are surfaced
- model identity and evaluation metadata are displayed in the UI

Remaining limitation: the reported confidence values are not calibrated operational probabilities.

### 7. Terminology inconsistency risk

The wording is now mostly aligned with the demonstrator brief:

- decision support
- readiness
- predicted risk
- simulated scenario
- human-in-the-loop

The paper should continue to avoid:

- autonomous control
- validated deployment
- guaranteed operational savings
- production-certified system

### 8. Reviewer attack points

The strongest likely reviewer attacks are still:

1. synthetic-data fidelity and possible task simplification
2. lack of real operational validation
3. limited probability calibration evidence
4. heuristic nature of fusion and action policies
5. weaker inventory macro precision despite good overall accuracy

Those critiques do not invalidate the demonstrator, but they do constrain the claims that can be made.

## D. Paper-Readiness Audit

### Figures

The repository now includes export-ready evaluation figures and a publication-oriented architecture figure:

- model comparison plots
- confusion matrices
- feature-importance plots
- maintenance RUL scatter plot
- system architecture figure

The full list is indexed in `D:\OCC-Demo\paper_assets\reports\artifact_index.md`.

Still missing:

- manually curated GUI screenshots captured from the running final demonstrator
- a final figure selection decision for the paper body versus appendix

### Tables

The repository now includes:

- per-module model comparison tables
- holdout metric JSON files
- feature-importance tables
- `module_evaluation_summary.csv`
- `panel_truthfulness_map.csv`

This is sufficient to support a system-paper methods and evaluation section.

### Module evaluation

The demonstrator is now much closer to paper-ready at module level.

Current exported holdout results:

- maintenance failure model: ROC-AUC 0.657 on final holdout
- maintenance urgency model: macro F1 0.846 and ROC-AUC OVR 0.975 on final holdout
- maintenance remaining-flights proxy: RMSE 4.147 and R2 0.921 on final holdout
- inventory risk model: macro F1 0.660 and ROC-AUC OVR 0.964 on final holdout
- bottleneck model: macro F1 0.691 and ROC-AUC OVR 0.959 on final holdout

These are acceptable demonstrator-level results for synthetic tabular tasks, but they should not be presented as real-world operational performance.

### System evaluation

System evaluation remains architecture-level rather than operationally validated. The paper can honestly claim:

- integrated end-to-end local demonstrator behavior
- deterministic scenario recomputation
- modular local inference
- transparent fusion and human-in-the-loop action support

The paper cannot honestly claim:

- airline deployment benefit
- validated delay savings produced by this software
- real assistance localization capability
- certified maintenance planning performance

### Reproducibility

This area is now strong enough for a capstone systems paper:

- saved model artifacts are local
- regeneration scripts exist
- evaluation tables and figures are exported
- split policy is fixed and documented
- provenance is explicit

The reproducibility note is provided in `D:\OCC-Demo\paper_assets\reports\reproducibility_notes.md`.

### Architecture clarity

Architecture clarity has improved materially. The current frontend architecture page and exported architecture figure now match the intended four-layer framing:

1. aircraft-side information layer
2. predictive/analytical module layer
3. OCC fusion layer
4. operator-facing interface

### Limitations disclosure

The demonstrator now contains explicit limitations disclosure in the interface and supporting reports. This was previously too weak for paper writing and is now at an acceptable baseline.

## Implemented Upgrades

The following upgrades were implemented after the audit:

- fixed 80% development and 20% final holdout workflow for trained modules
- cross-validation and hyperparameter tuning restricted to the development split
- candidate-model comparison for maintenance, inventory, and bottleneck modules
- saved local model bundles for all trained ML-backed modules
- holdout metrics, comparison tables, and feature-importance exports
- publication-grade architecture figure export
- provenance metadata in backend responses and frontend panels
- explicit rule-based treatment of passenger assistance readiness
- scenario-to-module API adapters so scenario payloads can be posted directly to prediction routes
- startup logic changed so the backend only regenerates artifacts when required files are missing
- artifact indexing, truthfulness mapping, and evaluation summary generation scripts

## What Still Cannot Be Claimed Honestly

The following claims would still be scientifically indefensible:

- that the demonstrator is validated on airline operational data
- that the reported metrics represent real-world airline performance
- that the assistance module performs true localization ML
- that the proactive-versus-reactive comparison is an empirically measured deployment effect
- that the fusion engine is an optimized or validated airline dispatch policy
- that the maintenance remaining-flights estimate is a certified RUL model

## Recommendation

The demonstrator is now suitable to support paper writing if the paper is framed as:

- an integrated local OCC decision-support research demonstrator
- a human-in-the-loop system architecture
- a synthetic but operationally grounded evaluation environment
- a platform demonstrating how trained module outputs can be fused into OCC advisory workflows

The paper should not be framed as operational validation. Within that boundary, the system is now strong enough for honest PhD-level writing, provided the limitations section is explicit and the paper distinguishes trained inference, rule-based logic, and scenario simulation throughout.
