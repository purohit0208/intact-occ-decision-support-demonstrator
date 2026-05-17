import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { FlightCard } from "../components/FlightCard";
import { FlightTable } from "../components/FlightTable";
import { SummaryCards } from "../components/SummaryCards";
import { fetchDemoFlights } from "../lib/api";
import { computeDashboardMetrics } from "../lib/readiness";
import type { FlightSummary } from "../types/flight";

export function Dashboard() {
  const navigate = useNavigate();
  const [flights, setFlights] = useState<FlightSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    fetchDemoFlights()
      .then((response) => {
        if (mounted) {
          setFlights(response.flights);
        }
      })
      .finally(() => {
        if (mounted) {
          setLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  const metrics = computeDashboardMetrics(flights);

  return (
    <div className="space-y-4">
      <section className="panel p-5">
        <div className="muted-label">Dashboard</div>
        <h2 className="mt-2 text-2xl font-semibold text-white">Inbound OCC coordination overview</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
          A local, human-in-the-loop research demonstrator for pre-arrival turnaround coordination. All flight identifiers
          are synthetic.
        </p>
      </section>

      <SummaryCards metrics={metrics} />

      <div className="hidden lg:block">
        <FlightTable flights={flights} onSelect={(flightId) => navigate(`/flight/${flightId}`)} />
      </div>

      <div className="grid gap-3 lg:hidden">
        {flights.map((flight) => (
          <FlightCard key={flight.id} flight={flight} onSelect={(flightId) => navigate(`/flight/${flightId}`)} />
        ))}
      </div>
      <p className="text-sm text-slate-400">
        {loading ? "Loading local flight cases." : "Select a synthetic flight for drilldown, or use Scenario Lab for what-if changes."}
      </p>
    </div>
  );
}
