import { fallbackFlightSummaries, scenarioLabSeed } from "../data/demoFlights";
import { fallbackScenarioPresets } from "../data/demoScenarios";
import type { ActionItem } from "../types/actions";
import type { BottleneckDistribution, BottleneckPrediction } from "../types/bottleneck";
import type {
  DemoFlightsResponse,
  DemoScenariosResponse,
  FlightDetailResponse,
  FlightSummary,
  FusionPrediction,
  ReadinessFactor,
  RecomputeResponse,
  ScenarioInput,
} from "../types/flight";
import type { InventoryPrediction } from "../types/inventory";
import type { MaintenancePrediction } from "../types/maintenance";
import type { ProvenanceInfo } from "../types/provenance";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

const toString = (value: unknown, fallback = "") => (typeof value === "string" && value.trim() ? value : fallback);
const toBoolean = (value: unknown, fallback = false) => (typeof value === "boolean" ? value : fallback);
const toNumber = (value: unknown, fallback = 0) => {
  const numeric = typeof value === "number" ? value : Number(value);
  return Number.isFinite(numeric) ? numeric : fallback;
};
const toStringArray = (value: unknown, fallback: string[] = []) =>
  Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : fallback;

function normalizeProvenance(input: Partial<ProvenanceInfo> | undefined, fallback: ProvenanceInfo): ProvenanceInfo {
  return {
    category:
      input?.category === "trained_ml_inference" ||
      input?.category === "rule_based_logic" ||
      input?.category === "scenario_simulation" ||
      input?.category === "fallback_placeholder"
        ? input.category
        : fallback.category,
    label: toString(input?.label, fallback.label),
    summary: toString(input?.summary, fallback.summary),
    selected_model: toString(input?.selected_model, fallback.selected_model ?? ""),
    development_metric: toString(input?.development_metric, fallback.development_metric ?? ""),
    test_metric: toString(input?.test_metric, fallback.test_metric ?? ""),
  };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`Request failed for ${path}: ${response.status}`);
  }

  return (await response.json()) as T;
}

function normalizeScenario(input: Partial<ScenarioInput> | undefined, fallback: ScenarioInput = scenarioLabSeed): ScenarioInput {
  return {
    ...fallback,
    ...input,
    id: toString(input?.id, fallback.id),
    flight_number: toString(input?.flight_number, fallback.flight_number),
    aircraft_type: toString(input?.aircraft_type, fallback.aircraft_type),
    route: toString(input?.route, fallback.route),
    route_class: toString(input?.route_class, fallback.route_class),
    eta: toString(input?.eta, fallback.eta),
    gate: toString(input?.gate, fallback.gate),
    passenger_load: toNumber(input?.passenger_load, fallback.passenger_load),
    arrival_delay: toNumber(input?.arrival_delay, fallback.arrival_delay),
    gate_congestion: toNumber(input?.gate_congestion, fallback.gate_congestion),
    assistance_request: toBoolean(input?.assistance_request, fallback.assistance_request),
    assistance_equipment_confirmed: toBoolean(
      input?.assistance_equipment_confirmed,
      fallback.assistance_equipment_confirmed,
    ),
    assistance_localization_status: toString(
      input?.assistance_localization_status,
      fallback.assistance_localization_status,
    ),
    inventory_shortage_score: toNumber(input?.inventory_shortage_score, fallback.inventory_shortage_score),
    trolley_availability: toNumber(input?.trolley_availability, fallback.trolley_availability),
    service_profile: toString(input?.service_profile, fallback.service_profile),
    catering_complexity: toNumber(input?.catering_complexity, fallback.catering_complexity),
    turnaround_pressure: toNumber(input?.turnaround_pressure, fallback.turnaround_pressure),
    item_criticality: toNumber(input?.item_criticality, fallback.item_criticality),
    inventory_category: toString(input?.inventory_category, fallback.inventory_category),
    malfunction_count: toNumber(input?.malfunction_count, fallback.malfunction_count),
    malfunction_severity: toNumber(input?.malfunction_severity, fallback.malfunction_severity),
    component_type: toString(input?.component_type, fallback.component_type),
    aircraft_age_cycles: toNumber(input?.aircraft_age_cycles, fallback.aircraft_age_cycles),
    flight_duration_hr: toNumber(input?.flight_duration_hr, fallback.flight_duration_hr),
    cabin_temperature: toNumber(input?.cabin_temperature, fallback.cabin_temperature),
    humidity: toNumber(input?.humidity, fallback.humidity),
    cycles_since_install: toNumber(input?.cycles_since_install, fallback.cycles_since_install),
    wear_index: toNumber(input?.wear_index, fallback.wear_index),
    environmental_stress: toNumber(input?.environmental_stress, fallback.environmental_stress),
    weather_disturbance: toNumber(input?.weather_disturbance, fallback.weather_disturbance),
    refueling_required: toBoolean(input?.refueling_required, fallback.refueling_required),
    cabin_report_notes: toStringArray(input?.cabin_report_notes, fallback.cabin_report_notes),
    reported_components: toStringArray(input?.reported_components, fallback.reported_components),
  };
}

function normalizeMaintenance(input: Partial<MaintenancePrediction> | undefined, scenario: ScenarioInput): MaintenancePrediction {
  return {
    failure_probability: toNumber(input?.failure_probability, 0),
    confidence: toNumber(input?.confidence, 0.5),
    remaining_flights_estimate: toNumber(input?.remaining_flights_estimate, 0),
    urgency_class:
      input?.urgency_class === "CRITICAL" ||
      input?.urgency_class === "SOON" ||
      input?.urgency_class === "PLAN" ||
      input?.urgency_class === "OK"
        ? input.urgency_class
        : "OK",
    anomaly_flag: toBoolean(input?.anomaly_flag, false),
    affected_components: toStringArray(input?.affected_components, scenario.reported_components),
    top_factors: toStringArray(input?.top_factors, []),
    explanation: toString(
      input?.explanation,
      "Maintenance assessment is unavailable, so a conservative fallback explanation is being shown.",
    ),
    recommended_action: toString(
      input?.recommended_action,
      "Continue operator review and monitor the reported component condition.",
    ),
    model_source: toString(input?.model_source, "local fallback"),
    provenance: normalizeProvenance(input?.provenance, {
      category: "rule_based_logic",
      label: "Rule-based logic",
      summary: "Fallback maintenance scoring is active because the backend did not return model provenance.",
      selected_model: "",
      development_metric: "",
      test_metric: "",
    }),
  };
}

function normalizeInventory(input: Partial<InventoryPrediction> | undefined, scenario: ScenarioInput): InventoryPrediction {
  const riskLevel =
    input?.risk_level === "HIGH" || input?.risk_level === "ELEVATED" || input?.risk_level === "LOW"
      ? input.risk_level
      : "LOW";

  return {
    shortage_risk: toNumber(input?.shortage_risk, 0),
    risk_level: riskLevel,
    affected_service_area: toString(input?.affected_service_area, scenario.inventory_category),
    confidence: toNumber(input?.confidence, 0.5),
    trolley_status: toString(input?.trolley_status, "Unknown"),
    top_factors: toStringArray(input?.top_factors, []),
    recommendation: toString(
      input?.recommendation,
      "Continue operator review of the current inventory and trolley state.",
    ),
    explanation: toString(
      input?.explanation,
      "Inventory assessment is unavailable, so a conservative fallback explanation is being shown.",
    ),
    model_source: toString(input?.model_source, "local fallback"),
    provenance: normalizeProvenance(input?.provenance, {
      category: "rule_based_logic",
      label: "Rule-based logic",
      summary: "Fallback inventory scoring is active because the backend did not return model provenance.",
      selected_model: "",
      development_metric: "",
      test_metric: "",
    }),
  };
}

function normalizeProbabilities(input: Partial<BottleneckDistribution> | undefined): BottleneckDistribution {
  const maintenance = toNumber(input?.Maintenance, 0.2);
  const catering = toNumber(input?.Catering, 0.2);
  const cleaning = toNumber(input?.Cleaning, 0.2);
  const boarding = toNumber(input?.Boarding, 0.2);
  const refueling = toNumber(input?.Refueling, 0.2);
  const total = maintenance + catering + cleaning + boarding + refueling || 1;

  return {
    Maintenance: maintenance / total,
    Catering: catering / total,
    Cleaning: cleaning / total,
    Boarding: boarding / total,
    Refueling: refueling / total,
  };
}

function normalizeBottleneck(
  input: Partial<BottleneckPrediction> | undefined,
  scenario: ScenarioInput,
): BottleneckPrediction {
  const probabilities = normalizeProbabilities(input?.probabilities);
  const dominant =
    input?.dominant_bottleneck &&
    ["Maintenance", "Catering", "Cleaning", "Boarding", "Refueling"].includes(input.dominant_bottleneck)
      ? input.dominant_bottleneck
      : scenario.inventory_shortage_score > 6
        ? "Catering"
        : scenario.malfunction_severity > 6
          ? "Maintenance"
          : "Boarding";

  return {
    probabilities,
    dominant_bottleneck: dominant as BottleneckPrediction["dominant_bottleneck"],
    confidence: toNumber(input?.confidence, Math.max(...Object.values(probabilities))),
    top_contributing_factors: toStringArray(input?.top_contributing_factors, []),
    explanation: toString(
      input?.explanation,
      "Bottleneck assessment is unavailable, so a conservative fallback explanation is being shown.",
    ),
    recommended_response: toString(
      input?.recommended_response,
      "Continue operator review and prepare the responsible turnaround team conservatively.",
    ),
    model_source: toString(input?.model_source, "local fallback"),
    provenance: normalizeProvenance(input?.provenance, {
      category: "rule_based_logic",
      label: "Rule-based logic",
      summary: "Fallback bottleneck scoring is active because the backend did not return model provenance.",
      selected_model: "",
      development_metric: "",
      test_metric: "",
    }),
  };
}

function normalizeReadinessBreakdown(
  input: Partial<ReadinessFactor>[] | undefined,
  fusion: Partial<FusionPrediction> | undefined,
): ReadinessFactor[] {
  if (Array.isArray(input) && input.length > 0) {
    return input.map((factor) => ({
      label: toString(factor.label, "Readiness factor"),
      impact: toNumber(factor.impact, 0),
      detail: toString(factor.detail, "No additional detail was returned."),
    }));
  }

  return [
    {
      label: "Overall readiness",
      impact: Math.max(0, 100 - toNumber(fusion?.readiness_score, 62)),
      detail: "Fallback readiness explanation is being shown because the backend did not return a detailed breakdown.",
    },
  ];
}

function normalizeFusion(input: Partial<FusionPrediction> | undefined): FusionPrediction {
  const actions: ActionItem[] = Array.isArray(input?.action_queue)
    ? input.action_queue.map((action) => ({
        priority:
          action.priority === "P1" || action.priority === "P2" || action.priority === "P3" || action.priority === "P4"
            ? action.priority
            : "P4",
        team: toString(action.team, "OCC Supervisor"),
        description: toString(action.description, "Maintain operator review of the current scenario."),
        rationale: toString(action.rationale, "No additional rationale was returned."),
        expected_impact: toString(action.expected_impact, "Supports conservative operator oversight."),
      }))
    : [];

  return {
    readiness_score: toNumber(input?.readiness_score, 62),
    criticality_score: toNumber(input?.criticality_score, 54),
    alert_level:
      input?.alert_level === "Critical" ||
      input?.alert_level === "Priority" ||
      input?.alert_level === "Watch" ||
      input?.alert_level === "Routine"
        ? input.alert_level
        : "Watch",
    at_risk: toBoolean(input?.at_risk, true),
    alert_summary: toStringArray(input?.alert_summary, [
      "Fallback local fusion is being displayed because the backend is unavailable.",
    ]),
    readiness_breakdown: normalizeReadinessBreakdown(input?.readiness_breakdown, input),
    action_queue: actions,
    expected_delay_risk_min: toNumber(input?.expected_delay_risk_min, 5.2),
    expected_benefit_min: toNumber(input?.expected_benefit_min, 1.0),
    proactive_vs_reactive_delta_min: toNumber(input?.proactive_vs_reactive_delta_min, 2.2),
    explanation: toString(
      input?.explanation,
      "Fallback fusion is being displayed because the backend is unavailable.",
    ),
    provenance: normalizeProvenance(input?.provenance, {
      category: "rule_based_logic",
      label: "Rule-based logic",
      summary: "Fallback fusion logic is active because the backend did not return provenance metadata.",
      selected_model: "",
      development_metric: "",
      test_metric: "",
    }),
  };
}

function normalizeFlightSummary(input: Partial<FlightSummary>): FlightSummary {
  const fallback = fallbackFlightSummaries[0];
  return {
    id: toString(input.id, fallback.id),
    flight_number: toString(input.flight_number, fallback.flight_number),
    aircraft_type: toString(input.aircraft_type, fallback.aircraft_type),
    route: toString(input.route, fallback.route),
    eta: toString(input.eta, fallback.eta),
    gate: toString(input.gate, fallback.gate),
    arrival_delay: toNumber(input.arrival_delay, fallback.arrival_delay),
    readiness_score: toNumber(input.readiness_score, fallback.readiness_score),
    dominant_bottleneck: toString(input.dominant_bottleneck, fallback.dominant_bottleneck),
    maintenance_urgency: toString(input.maintenance_urgency, fallback.maintenance_urgency),
    inventory_alert_status: toString(input.inventory_alert_status, fallback.inventory_alert_status),
    passenger_assistance_status: toString(input.passenger_assistance_status, fallback.passenger_assistance_status),
    alert_level: toString(input.alert_level, fallback.alert_level),
    at_risk: toBoolean(input.at_risk, fallback.at_risk),
  };
}

function normalizeFlightDetailResponse(
  input: Partial<FlightDetailResponse> | Partial<RecomputeResponse>,
  fallbackScenario: ScenarioInput = scenarioLabSeed,
): FlightDetailResponse {
  const scenario = normalizeScenario(input.scenario, fallbackScenario);
  const maintenance = normalizeMaintenance(input.maintenance, scenario);
  const inventory = normalizeInventory(input.inventory, scenario);
  const bottleneck = normalizeBottleneck(input.bottleneck, scenario);
  const fusion = normalizeFusion(input.fusion);

  return { scenario, maintenance, inventory, bottleneck, fusion };
}

export async function fetchDemoFlights(): Promise<DemoFlightsResponse> {
  try {
    const response = await request<DemoFlightsResponse>("/demo/flights");
    return { flights: response.flights.map((flight) => normalizeFlightSummary(flight)) };
  } catch {
    return { flights: fallbackFlightSummaries.map((flight) => normalizeFlightSummary(flight)) };
  }
}

export async function fetchFlightDetail(flightId: string): Promise<FlightDetailResponse> {
  try {
    const response = await request<FlightDetailResponse>(`/demo/flights/${flightId}`);
    const matchedFallback = fallbackScenarioPresets.find((preset) => preset.id === flightId)?.scenario ?? scenarioLabSeed;
    return normalizeFlightDetailResponse(response, matchedFallback);
  } catch {
    const matchedScenario = fallbackScenarioPresets.find((preset) => preset.id === flightId)?.scenario;
    if (!matchedScenario) {
      throw new Error(`Unknown flight id: ${flightId}`);
    }
    return recomputeScenario(matchedScenario);
  }
}

export async function fetchDemoScenarios(): Promise<DemoScenariosResponse> {
  try {
    const response = await request<DemoScenariosResponse>("/demo/scenarios");
    return {
      scenarios: response.scenarios.map((scenario) => {
        const fallback = fallbackScenarioPresets.find((preset) => preset.id === scenario.id)?.scenario ?? scenarioLabSeed;
        return normalizeScenario(scenario, fallback);
      }),
    };
  } catch {
    return { scenarios: fallbackScenarioPresets.map((preset) => normalizeScenario(preset.scenario, preset.scenario)) };
  }
}

export async function recomputeScenario(scenario: ScenarioInput): Promise<RecomputeResponse> {
  const normalizedScenario = normalizeScenario(scenario, scenarioLabSeed);
  const payload = {
    ...normalizedScenario,
    assistance_equipment_confirmed: normalizedScenario.assistance_request
      ? normalizedScenario.assistance_equipment_confirmed
      : false,
  };

  try {
    const response = await request<RecomputeResponse>("/scenario/recompute", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    return normalizeFlightDetailResponse(response, payload);
  } catch {
    return normalizeFlightDetailResponse(
      {
        scenario: payload,
        maintenance: {
          failure_probability: Math.min(0.92, 0.1 + payload.malfunction_severity * 0.07 + payload.wear_index * 0.005),
          confidence: 0.62,
          remaining_flights_estimate: Math.max(
            2,
            Math.round(46 - payload.cycles_since_install / 120 - payload.malfunction_severity * 2),
          ),
          urgency_class:
            payload.malfunction_severity >= 7
              ? "CRITICAL"
              : payload.malfunction_severity >= 5
                ? "SOON"
                : payload.malfunction_severity >= 3
                ? "PLAN"
                  : "OK",
          anomaly_flag: payload.malfunction_severity >= 7,
          affected_components: payload.reported_components.length ? payload.reported_components : [payload.component_type],
          top_factors: ["Fallback maintenance scoring", "Backend unavailable"],
          explanation: "Fallback local scoring is being shown because the backend endpoint is unavailable.",
          recommended_action: "Start the backend to access the full local inference pipeline.",
          model_source: "frontend fallback",
          provenance: {
            category: "fallback_placeholder",
            label: "Offline fallback",
            summary: "Frontend fallback maintenance scoring is active because the backend is unavailable.",
            selected_model: "",
            development_metric: "",
            test_metric: "",
          },
        },
        inventory: {
          shortage_risk: Math.min(
            0.95,
            0.08 + payload.inventory_shortage_score * 0.07 + (1 - payload.trolley_availability) * 0.35,
          ),
          risk_level:
            payload.inventory_shortage_score >= 7
              ? "HIGH"
              : payload.inventory_shortage_score >= 4
                ? "ELEVATED"
                : "LOW",
          affected_service_area: payload.inventory_category,
          confidence: 0.58,
          trolley_status:
            payload.trolley_availability < 0.35
              ? "Unavailable"
              : payload.trolley_availability < 0.62
                ? "Constrained"
                : "Available",
          top_factors: ["Fallback inventory scoring", "Backend unavailable"],
          recommendation: "Start the backend to access the trained inventory model and fuller rule set.",
          explanation: "Fallback local scoring is being shown because the backend endpoint is unavailable.",
          model_source: "frontend fallback",
          provenance: {
            category: "fallback_placeholder",
            label: "Offline fallback",
            summary: "Frontend fallback inventory scoring is active because the backend is unavailable.",
            selected_model: "",
            development_metric: "",
            test_metric: "",
          },
        },
        bottleneck: {
          probabilities: {
            Maintenance: 0.25,
            Catering: 0.22,
            Cleaning: 0.16,
            Boarding: 0.27,
            Refueling: 0.1,
          },
          dominant_bottleneck: "Boarding",
          confidence: 0.27,
          top_contributing_factors: ["fallback local scoring"],
          explanation: "Fallback bottleneck distribution is being shown because the backend endpoint is unavailable.",
          recommended_response: "Start the backend to restore the trained bottleneck classifier and full decision-support flow.",
          model_source: "frontend fallback",
          provenance: {
            category: "fallback_placeholder",
            label: "Offline fallback",
            summary: "Frontend fallback bottleneck scoring is active because the backend is unavailable.",
            selected_model: "",
            development_metric: "",
            test_metric: "",
          },
        },
        fusion: {
          readiness_score: 62,
          criticality_score: 54,
          alert_level: "Watch",
          at_risk: true,
          alert_summary: ["Start the backend to access the full local fusion engine and action queue."],
          readiness_breakdown: [
            {
              label: "Backend unavailable",
              impact: 38,
              detail: "The frontend is using a conservative fallback response because the backend is not running.",
            },
          ],
          action_queue: [
            {
              priority: "P4",
              team: "OCC Supervisor",
              description: "Start the backend service to enable the full local decision-support demonstrator.",
              rationale: "The frontend is currently using a limited fallback response.",
              expected_impact: "Restores full local inference, fusion logic, and demo data services.",
            },
          ],
          expected_delay_risk_min: 5.2,
          expected_benefit_min: 1.0,
          proactive_vs_reactive_delta_min: 2.2,
          explanation: "Fallback fusion is being displayed because the backend is unavailable.",
          provenance: {
            category: "fallback_placeholder",
            label: "Offline fallback",
            summary: "Frontend fallback fusion logic is active because the backend is unavailable.",
            selected_model: "",
            development_metric: "",
            test_metric: "",
          },
        },
      },
      payload,
    );
  }
}

export const defaultScenarioSeed = scenarioLabSeed;
