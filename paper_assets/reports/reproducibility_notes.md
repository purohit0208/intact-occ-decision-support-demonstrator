# Reproducibility Notes

## Scope

These notes describe how to regenerate the trained-model artifacts, evaluation tables, and publication assets for the INTACT OCC research demonstrator.

## Environment

- Windows laptop
- local Python environment
- local frontend toolchain
- no cloud services
- no external APIs
- no authentication
- no database

## Core Commands

From `<repo-root>`:

### Backend dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Frontend dependencies

```powershell
cd <repo-root>\frontend
npm install
```

### Run the local demonstrator

```powershell
cd <repo-root>\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second window:

```powershell
cd <repo-root>\frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

### Regenerate all training and publication artifacts

```powershell
cd <repo-root>\backend
python -m app.training.train_all
```

### Regenerate publication assets only

```powershell
cd <repo-root>\backend
python -m app.training.generate_publication_assets
```

## Split Policy

All trained ML modules now follow the same evaluation policy:

- fixed 80% development split
- fixed 20% final holdout test split
- cross-validation and hyperparameter tuning only within the 80% development split

This policy is encoded in the training scripts and written into the saved metadata.

## Trained Modules

### Predictive maintenance

- binary task for near-term failure probability
- multiclass task for urgency class
- regression task for remaining-flights proxy

### Inventory intelligence

- multiclass classification of inventory risk level
- transparent post-model operational logic for affected area and recommendation

### Bottleneck prediction

- multiclass classification over maintenance, catering, cleaning, boarding, and refueling bottleneck classes

### Assistance readiness

- intentionally rule-based only
- not claimed as trained ML

## Artifact Locations

### Saved models

- `<repo-root>\backend\app\models\maintenance_bundle.joblib`
- `<repo-root>\backend\app\models\inventory_bundle.joblib`
- `<repo-root>\backend\app\models\bottleneck_bundle.joblib`

### Evaluation tables

- `<repo-root>\paper_assets\tables`

### Figures

- `<repo-root>\paper_assets\figures`

### Reports

- `<repo-root>\paper_assets\reports`

## Notes on Determinism

The data generators and train/test split procedures use fixed seeds. This makes the synthetic datasets and the development/test partitions reproducible within the local environment.

## Important Limits

- synthetic data does not establish operational validation
- confidence values are not calibrated deployment probabilities
- action logic is heuristic and transparent by design
- UI fallback mode must not be used for evaluation claims

