export type ProvenanceCategory =
  | "trained_ml_inference"
  | "rule_based_logic"
  | "scenario_simulation"
  | "fallback_placeholder";

export interface ProvenanceInfo {
  category: ProvenanceCategory;
  label: string;
  summary: string;
  selected_model?: string | null;
  development_metric?: string | null;
  test_metric?: string | null;
}
