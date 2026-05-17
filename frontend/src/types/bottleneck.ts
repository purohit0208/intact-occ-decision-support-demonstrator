import type { ProvenanceInfo } from "./provenance";

export interface BottleneckDistribution {
  Maintenance: number;
  Catering: number;
  Cleaning: number;
  Boarding: number;
  Refueling: number;
}

export type BottleneckLabel = keyof BottleneckDistribution;

export interface BottleneckPrediction {
  probabilities: BottleneckDistribution;
  dominant_bottleneck: BottleneckLabel;
  confidence: number;
  top_contributing_factors: string[];
  explanation: string;
  recommended_response: string;
  model_source: string;
  provenance: ProvenanceInfo;
}
