import type { FlightDetailResponse } from "../types/flight";
import { formatMaintenanceStatus } from "./format";

function csvEscape(value: string | number | boolean | null | undefined) {
  const stringValue = value == null ? "" : String(value);
  if (/[",\n]/.test(stringValue)) {
    return `"${stringValue.replace(/"/g, '""')}"`;
  }
  return stringValue;
}

export function buildBriefingCsv(detail: FlightDetailResponse) {
  const rows: Array<[string, string | number | boolean]> = [
    ["Flight number", detail.scenario.flight_number],
    ["Aircraft type", detail.scenario.aircraft_type],
    ["Route", detail.scenario.route],
    ["ETA", detail.scenario.eta],
    ["Gate", detail.scenario.gate],
    ["Passenger load", detail.scenario.passenger_load],
    ["Arrival delay min", detail.scenario.arrival_delay],
    ["Gate congestion", detail.scenario.gate_congestion],
    ["Assistance request", detail.scenario.assistance_request],
    ["Assistance confirmed", detail.scenario.assistance_equipment_confirmed],
    ["Maintenance status", formatMaintenanceStatus(detail.maintenance.urgency_class)],
    ["Maintenance failure probability", detail.maintenance.failure_probability],
    ["Remaining flights estimate", detail.maintenance.remaining_flights_estimate],
    ["Inventory risk level", detail.inventory.risk_level],
    ["Inventory shortage risk", detail.inventory.shortage_risk],
    ["Dominant bottleneck", detail.bottleneck.dominant_bottleneck],
    ["Readiness score", detail.fusion.readiness_score],
    ["Criticality score", detail.fusion.criticality_score],
    ["Alert level", detail.fusion.alert_level],
    ["Expected delay risk min", detail.fusion.expected_delay_risk_min],
    ["Expected benefit min", detail.fusion.expected_benefit_min],
    ["Alert summary", detail.fusion.alert_summary.join(" | ")],
    [
      "Action queue",
      detail.fusion.action_queue
        .map((action) => `${action.priority} ${action.team}: ${action.description}`)
        .join(" | "),
    ],
  ];

  return [["Field", "Value"], ...rows]
    .map((row) => row.map(csvEscape).join(","))
    .join("\n");
}

export function downloadCsv(filename: string, content: string) {
  const blob = new Blob([content], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
