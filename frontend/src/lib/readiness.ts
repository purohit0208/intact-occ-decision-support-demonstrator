import type { BottleneckDistribution } from "../types/bottleneck";
import type { DashboardMetric, FlightSummary } from "../types/flight";

export const bottleneckEntries = (probabilities: BottleneckDistribution) =>
  Object.entries(probabilities).map(([name, value]) => ({ name, value: Math.round(value * 100) }));

export function computeDashboardMetrics(flights: FlightSummary[]): DashboardMetric[] {
  const atRisk = flights.filter((flight) => flight.at_risk).length;
  const criticalMaintenance = flights.filter((flight) => flight.maintenance_urgency === "CRITICAL").length;
  const averageReadiness =
    flights.length > 0
      ? flights.reduce((total, flight) => total + flight.readiness_score, 0) / flights.length
      : 0;

  return [
    { label: "Inbound flights", value: String(flights.length), tone: "neutral" },
    { label: "Flights at risk", value: String(atRisk), tone: atRisk > 2 ? "critical" : "warning" },
    { label: "Critical maintenance alerts", value: String(criticalMaintenance), tone: criticalMaintenance ? "critical" : "good" },
    { label: "Average readiness score", value: averageReadiness.toFixed(1), tone: averageReadiness < 70 ? "warning" : "good" },
  ];
}
