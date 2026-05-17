import type { ReadinessFactor } from "../types/flight";

interface ReadinessBreakdownProps {
  factors: ReadinessFactor[];
  maxItems?: number;
}

export function ReadinessBreakdown({ factors, maxItems = 4 }: ReadinessBreakdownProps) {
  const visible = factors.filter((factor) => factor.impact > 0.1).slice(0, maxItems);

  return (
    <section className="panel p-5">
      <div className="muted-label">Readiness explanation</div>
      <h3 className="mt-2 panel-title">Contributing factors</h3>
      <div className="mt-5 space-y-3">
        {visible.length === 0 ? (
          <div className="rounded-2xl border border-panelEdge/80 bg-slate-950/35 p-4 text-sm text-slate-300">
            The current scenario has no material readiness deductions beyond routine monitoring.
          </div>
        ) : null}
        {visible.map((factor) => (
          <div key={factor.label} className="rounded-2xl border border-panelEdge/80 bg-slate-950/35 p-4">
            <div className="flex items-center justify-between gap-3">
              <div className="text-sm font-semibold text-white">{factor.label}</div>
              <div className="text-sm font-semibold text-amber-200">-{factor.impact.toFixed(1)}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
