import type { FlightSummary } from "../types/flight";
import { formatDelay, formatScore } from "../lib/format";
import { RiskBadge } from "./RiskBadge";

interface FlightCardProps {
  flight: FlightSummary;
  onSelect: (flightId: string) => void;
}

export function FlightCard({ flight, onSelect }: FlightCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect(flight.id)}
      className="panel w-full p-4 text-left transition hover:border-signal.cyan/30 hover:bg-slate-900/70"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-lg font-semibold text-white">{flight.flight_number}</div>
          <div className="text-sm text-slate-400">
            {flight.aircraft_type} | {flight.route}
          </div>
        </div>
        <RiskBadge label={flight.alert_level} />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div>
          <div className="muted-label">ETA / Gate</div>
          <div className="mt-1 text-white">
            {flight.eta} | {flight.gate}
          </div>
        </div>
        <div>
          <div className="muted-label">Arrival delay</div>
          <div className="mt-1 text-white">{formatDelay(flight.arrival_delay)}</div>
        </div>
        <div>
          <div className="muted-label">Readiness</div>
          <div className="mt-1 text-white">{formatScore(flight.readiness_score)}</div>
        </div>
        <div>
          <div className="muted-label">Bottleneck</div>
          <div className="mt-1 text-white">{flight.dominant_bottleneck}</div>
        </div>
      </div>
    </button>
  );
}
