import clsx from "clsx";

import type { DashboardMetric } from "../types/flight";

interface SummaryCardsProps {
  metrics: DashboardMetric[];
}

const toneMap: Record<DashboardMetric["tone"], string> = {
  neutral: "from-slate-800/90 to-slate-900/80",
  good: "from-emerald-950/90 to-slate-900/80",
  warning: "from-amber-950/90 to-slate-900/80",
  critical: "from-rose-950/90 to-slate-900/80",
};

export function SummaryCards({ metrics }: SummaryCardsProps) {
  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric) => (
        <div
          key={metric.label}
          className={clsx(
            "rounded-3xl border border-panelEdge/80 bg-gradient-to-br px-4 py-4 shadow-panel",
            toneMap[metric.tone],
          )}
        >
          <div className="muted-label">{metric.label}</div>
          <div className="mt-3 text-3xl font-semibold text-white">{metric.value}</div>
        </div>
      ))}
    </div>
  );
}
