import { Bar, BarChart, CartesianGrid, ResponsiveContainer, XAxis, YAxis } from "recharts";

import type { BottleneckPrediction } from "../types/bottleneck";
import { bottleneckEntries } from "../lib/readiness";
import { ExplanationCard } from "./ExplanationCard";
import { ProvenanceBadge } from "./ProvenanceBadge";
import { RiskBadge } from "./RiskBadge";

interface BottleneckPanelProps {
  bottleneck: BottleneckPrediction;
}

export function BottleneckPanel({ bottleneck }: BottleneckPanelProps) {
  const data = bottleneckEntries(bottleneck.probabilities);
  const factors = bottleneck.top_contributing_factors.length
    ? bottleneck.top_contributing_factors.join(", ")
    : "No contributing factors were returned.";

  return (
    <section className="panel p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="muted-label">Turnaround bottleneck prediction</div>
          <h3 className="mt-2 panel-title">Operational pressure distribution</h3>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <ProvenanceBadge provenance={bottleneck.provenance} />
          <RiskBadge label={bottleneck.dominant_bottleneck} tone="info" />
        </div>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-2xl border border-panelEdge/80 bg-slate-950/35 p-4">
          <div className="h-[260px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} layout="vertical" margin={{ top: 8, right: 12, left: 12, bottom: 8 }}>
                <CartesianGrid stroke="rgba(148, 163, 184, 0.12)" horizontal={false} />
                <XAxis type="number" stroke="#94a3b8" tickLine={false} axisLine={false} />
                <YAxis type="category" dataKey="name" stroke="#cbd5e1" tickLine={false} axisLine={false} width={80} />
                <Bar dataKey="value" fill="#54d1db" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="space-y-4">
          <ExplanationCard title="Contributing factors" body={factors} footnote={`Confidence: ${(bottleneck.confidence * 100).toFixed(1)}%.`} />
          <ExplanationCard title="Recommended response" body={bottleneck.recommended_response} />
        </div>
      </div>
    </section>
  );
}
