import type { ActionItem } from "./actions";
import type { BottleneckPrediction } from "./bottleneck";
import type { InventoryPrediction } from "./inventory";
import type { MaintenancePrediction } from "./maintenance";
import type { ProvenanceInfo } from "./provenance";

export interface ScenarioInput {
  id: string;
  flight_number: string;
  aircraft_type: string;
  route: string;
  route_class: string;
  eta: string;
  gate: string;
  passenger_load: number;
  arrival_delay: number;
  gate_congestion: number;
  assistance_request: boolean;
  assistance_equipment_confirmed: boolean;
  assistance_localization_status: string;
  inventory_shortage_score: number;
  trolley_availability: number;
  service_profile: string;
  catering_complexity: number;
  turnaround_pressure: number;
  item_criticality: number;
  inventory_category: string;
  malfunction_count: number;
  malfunction_severity: number;
  component_type: string;
  aircraft_age_cycles: number;
  flight_duration_hr: number;
  cabin_temperature: number;
  humidity: number;
  cycles_since_install: number;
  wear_index: number;
  environmental_stress: number;
  weather_disturbance: number;
  refueling_required: boolean;
  cabin_report_notes: string[];
  reported_components: string[];
}

export interface FusionPrediction {
  readiness_score: number;
  criticality_score: number;
  alert_level: "Routine" | "Watch" | "Priority" | "Critical";
  at_risk: boolean;
  alert_summary: string[];
  readiness_breakdown: ReadinessFactor[];
  action_queue: ActionItem[];
  expected_delay_risk_min: number;
  expected_benefit_min: number;
  proactive_vs_reactive_delta_min: number;
  explanation: string;
  provenance: ProvenanceInfo;
}

export interface ReadinessFactor {
  label: string;
  impact: number;
  detail: string;
}

export interface FlightSummary {
  id: string;
  flight_number: string;
  aircraft_type: string;
  route: string;
  eta: string;
  gate: string;
  arrival_delay: number;
  readiness_score: number;
  dominant_bottleneck: string;
  maintenance_urgency: string;
  inventory_alert_status: string;
  passenger_assistance_status: string;
  alert_level: string;
  at_risk: boolean;
}

export interface DemoFlightsResponse {
  flights: FlightSummary[];
}

export interface DemoScenariosResponse {
  scenarios: ScenarioInput[];
}

export interface FlightDetailResponse {
  scenario: ScenarioInput;
  maintenance: MaintenancePrediction;
  inventory: InventoryPrediction;
  bottleneck: BottleneckPrediction;
  fusion: FusionPrediction;
}

export interface RecomputeResponse extends FlightDetailResponse {}

export interface DashboardMetric {
  label: string;
  value: string;
  tone: "neutral" | "good" | "warning" | "critical";
}
