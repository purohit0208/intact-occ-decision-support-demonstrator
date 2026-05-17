export const impactReferenceMetrics = [
  { label: "Average turnaround delay reduction", value: "3 minutes" },
  { label: "Average additional completed flights per day", value: "0.11" },
  { label: "Daily turnaround cost savings", value: "about $966.95" },
  { label: "Daily additional revenue upper bound", value: "about $2714.29" },
  { label: "Payback period estimate", value: "about 1.5 years" },
];

export const architectureLayers = [
  {
    title: "Aircraft-side reporting layer",
    body: "Structured cabin reports, assistance requests, and inventory status indicators are transmitted before landing to give the OCC earlier operational visibility.",
  },
  {
    title: "Predictive maintenance, inventory, and bottleneck modules",
    body: "Local inference modules process synthetic but operationally grounded features and return conservative risk indicators and explanations.",
  },
  {
    title: "OCC fusion layer",
    body: "A transparent rule-based fusion engine combines module outputs into readiness scoring, alert prioritization, and recommended dispatch or coordination actions.",
  },
  {
    title: "Presentation layer",
    body: "The local GUI presents inbound flights, flight-level drilldown, a scenario lab, and impact framing suitable for research demonstration and academic discussion.",
  },
];

export const truthfulnessMatrix = [
  {
    panel: "Aircraft-side / cabin report panel",
    provenance: "Scenario simulation",
    note: "Pre-arrival cabin, assistance, and trolley signals are simulated but operationally grounded scenario inputs.",
  },
  {
    panel: "Predictive maintenance panel",
    provenance: "Trained ML inference",
    note: "Failure probability, urgency class, and remaining flights are produced by locally trained models using synthetic reliability-oriented data.",
  },
  {
    panel: "Inventory intelligence panel",
    provenance: "Trained ML inference + rule-based interpretation",
    note: "Risk level is ML-backed; affected area and operator recommendation remain transparent operational logic.",
  },
  {
    panel: "Passenger assistance panel",
    provenance: "Rule-based logic",
    note: "Assistance readiness is intentionally presented as dispatch-support logic rather than a localization ML model.",
  },
  {
    panel: "Bottleneck prediction panel",
    provenance: "Trained ML inference",
    note: "Dominant bottleneck and probability distribution are produced by a local multiclass model trained on process-aware synthetic turnaround scenarios.",
  },
  {
    panel: "Readiness score / action queue",
    provenance: "Rule-based logic",
    note: "Fusion outputs are deterministic, editable OCC logic built on module outputs and scenario state.",
  },
  {
    panel: "Impact page synthetic KPIs",
    provenance: "Scenario simulation",
    note: "Reactive versus proactive comparisons are demonstrator-level indicators rather than validated airline outcomes.",
  },
];

export const architectureNotes = [
  "Real-versus-simulated boundaries are surfaced explicitly in the interface through provenance badges and notes.",
  "All trained inference runs locally and loads saved model artifacts; no external APIs or cloud services are used.",
  "The demonstrator remains human-in-the-loop: no panel issues autonomous dispatch or operational control commands.",
];

export const limitationsDisclosure = [
  "All model evaluation artifacts are based on synthetic but operationally grounded data, not airline operational datasets.",
  "Confidence values are model outputs from local classifiers and should not be interpreted as calibrated operational probabilities without further validation.",
  "Fusion and action logic are transparent heuristics designed for demonstrator traceability, not optimized airline dispatch policies.",
];
