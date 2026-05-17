# Repository Scope and Evidence Boundary

This repository supports a local research demonstrator for aircraft turnaround decision support in an OCC context.

The repository contains:

- local FastAPI backend source code;
- local React/Vite frontend source code;
- synthetic training data and deterministic scenario data;
- saved local model bundles used by the demonstrator;
- training and publication-asset generation scripts;
- generated evaluation tables, provenance maps, figures, and audit notes.

The repository does not contain real airline operational data.

The repository does not provide production airline software, certified safety tooling, or validated operational deployment evidence. Predictive outputs are trained on synthetic but operationally grounded data. Passenger assistance readiness, OCC fusion, action queues, and proactive-versus-reactive comparisons are rule-based or scenario-level demonstrator logic and should be interpreted accordingly.

Any operational aviation use would require real-world data validation, safety assessment, human-factors evaluation, airline/airport process integration, and compliance with applicable aviation and AI governance requirements.
