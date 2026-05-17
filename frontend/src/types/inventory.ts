import type { ProvenanceInfo } from "./provenance";

export type InventoryRiskLevel = "LOW" | "ELEVATED" | "HIGH";

export interface InventoryPrediction {
  shortage_risk: number;
  risk_level: InventoryRiskLevel;
  affected_service_area: string;
  confidence: number;
  trolley_status: string;
  top_factors: string[];
  recommendation: string;
  explanation: string;
  model_source: string;
  provenance: ProvenanceInfo;
}
