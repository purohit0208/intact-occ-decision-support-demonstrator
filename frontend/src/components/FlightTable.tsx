import type { FlightSummary } from "../types/flight";
import { formatDelay, formatScore } from "../lib/format";
import { RiskBadge } from "./RiskBadge";

interface FlightTableProps {
  flights: FlightSummary[];
  onSelect: (flightId: string) => void;
}

export function FlightTable({ flights, onSelect }: FlightTableProps) {
  return (
    <div className="panel overflow-hidden">
      <div className="border-b border-panelEdge/80 px-5 py-4">
        <div className="panel-title">Inbound flight overview</div>
        <p className="mt-1 text-sm text-slate-400">
          Synthetic inbound cases with fused OCC readiness states.
        </p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-950/35 text-left text-xs uppercase tracking-[0.18em] text-slate-400">
            <tr>
              <th className="px-5 py-4">Flight</th>
              <th className="px-5 py-4">ETA / Gate</th>
              <th className="px-5 py-4">Arrival delay</th>
              <th className="px-5 py-4">Readiness</th>
              <th className="px-5 py-4">Dominant bottleneck</th>
              <th className="px-5 py-4">Maintenance</th>
              <th className="px-5 py-4">Inventory</th>
              <th className="px-5 py-4">Assistance</th>
            </tr>
          </thead>
          <tbody>
            {flights.map((flight) => (
              <tr
                key={flight.id}
                className="cursor-pointer border-t border-panelEdge/60 transition hover:bg-slate-950/35"
                onClick={() => onSelect(flight.id)}
              >
                <td className="px-5 py-4">
                  <div className="font-semibold text-white">{flight.flight_number}</div>
                  <div className="text-slate-400">{flight.aircraft_type}</div>
                </td>
                <td className="px-5 py-4">
                  <div className="text-white">{flight.eta}</div>
                  <div className="text-slate-400">{flight.gate}</div>
                </td>
                <td className="px-5 py-4 text-slate-200">{formatDelay(flight.arrival_delay)}</td>
                <td className="px-5 py-4">
                  <div className="font-semibold text-white">{formatScore(flight.readiness_score)}</div>
                  <div className="mt-1">
                    <RiskBadge label={flight.alert_level} />
                  </div>
                </td>
                <td className="px-5 py-4">
                  <RiskBadge label={flight.dominant_bottleneck} tone="info" />
                </td>
                <td className="px-5 py-4">
                  <RiskBadge label={flight.maintenance_urgency} />
                </td>
                <td className="px-5 py-4">
                  <RiskBadge label={flight.inventory_alert_status} />
                </td>
                <td className="px-5 py-4">
                  <RiskBadge label={flight.passenger_assistance_status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
