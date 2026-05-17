import type { ProvenanceInfo } from "./provenance";

export type UrgencyClass = "OK" | "PLAN" | "SOON" | "CRITICAL";

export interface MaintenancePrediction {
  failure_probability: number;
  confidence: number;
  remaining_flights_estimate: number;
  urgency_class: UrgencyClass;
  anomaly_flag: boolean;
  affected_components: string[];
  top_factors: string[];
  explanation: string;
  recommended_action: string;
  model_source: string;
  provenance: ProvenanceInfo;
}
