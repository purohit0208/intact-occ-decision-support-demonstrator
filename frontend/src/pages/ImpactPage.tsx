import { useEffect, useMemo, useState } from "react";

import { ExplanationCard } from "../components/ExplanationCard";
import { KPIWidgets } from "../components/KPIWidgets";
import { fetchDemoFlights } from "../lib/api";
import type { FlightSummary } from "../types/flight";

export function ImpactPage() {
  const [flights, setFlights] = useState<FlightSummary[]>([]);

  useEffect(() => {
    fetchDemoFlights().then((response) => setFlights(response.flights));
  }, []);

  const derived = useMemo(() => {
    const averageReadiness =
      flights.length > 0 ? flights.reduce((total, flight) => total + flight.readiness_score, 0) / flights.length : 0;
    const atRisk = flights.filter((flight) => flight.at_risk).length;
    return {
      averageReadiness,
      atRisk,
      proactiveGain: Math.max(1.8, Math.min(6.5, (100 - averageReadiness) / 12)),
      expectedDelayRisk: Math.max(3.2, Math.min(11.4, atRisk * 1.7)),
    };
  }, [flights]);

  return (
    <div className="space-y-4">
      <section className="panel p-5">
        <div className="muted-label">Impact page</div>
        <h2 className="mt-2 text-2xl font-semibold text-white">Proactive versus reactive coordination framing</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
          A compact view of simulated delay exposure and expected benefit. These indicators support discussion only and
          are not validated airline performance claims.
        </p>
      </section>

      <KPIWidgets
        items={[
          { label: "Flights currently at risk", value: String(derived.atRisk), note: "Based on the current default inbound cases." },
          { label: "Average readiness", value: derived.averageReadiness.toFixed(1), note: "Fused local demonstrator score." },
          { label: "Expected delay-risk indication", value: `${derived.expectedDelayRisk.toFixed(1)} min`, note: "Simulated current-state exposure." },
          { label: "Estimated response improvement", value: `${derived.proactiveGain.toFixed(1)} min`, note: "Simulated proactive versus reactive comparison." },
        ]}
      />

      <div className="grid gap-4 xl:grid-cols-[1fr_1fr]">
        <ExplanationCard
          title="Proactive coordination"
          body="Use pre-arrival signals to prepare maintenance, catering, PRM, or gate teams before the aircraft reaches the stand."
        />
        <ExplanationCard
          title="Reactive coordination"
          body="Wait until stand arrival, which leaves less time to resolve cabin, trolley, assistance, or bottleneck issues."
        />
      </div>
    </div>
  );
}
