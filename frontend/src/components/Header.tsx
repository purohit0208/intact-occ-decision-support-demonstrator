import { ActivitySquare, Cpu, ShieldCheck } from "lucide-react";

export function Header() {
  return (
    <header className="panel px-5 py-5 md:px-6">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <div className="muted-label">INTACT project context</div>
          <h1 className="mt-2 text-2xl font-semibold tracking-wide text-white md:text-3xl">
            INTACT OCC Decision Support Demonstrator
          </h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
            Local hybrid OCC research demonstrator for aircraft turnaround coordination. This interface presents
            conservative decision-support outputs only; the operator remains in the loop at all times.
          </p>
        </div>
        <div className="grid gap-3 sm:grid-cols-3">
          <div className="rounded-2xl border border-panelEdge bg-slate-950/40 px-4 py-3">
            <div className="flex items-center gap-2 text-sm font-medium text-white">
              <Cpu className="h-4 w-4 text-signal.cyan" />
              Local inference
            </div>
            <p className="mt-1 text-xs text-slate-400">Synthetic training data, local model loading, local fallback logic.</p>
          </div>
          <div className="rounded-2xl border border-panelEdge bg-slate-950/40 px-4 py-3">
            <div className="flex items-center gap-2 text-sm font-medium text-white">
              <ActivitySquare className="h-4 w-4 text-signal.amber" />
              Pre-arrival visibility
            </div>
            <p className="mt-1 text-xs text-slate-400">Aircraft-side reports are fused before landing for OCC review.</p>
          </div>
          <div className="rounded-2xl border border-panelEdge bg-slate-950/40 px-4 py-3">
            <div className="flex items-center gap-2 text-sm font-medium text-white">
              <ShieldCheck className="h-4 w-4 text-signal.coral" />
              Human in the loop
            </div>
            <p className="mt-1 text-xs text-slate-400">No autonomous dispatching, no external APIs, no production claims.</p>
          </div>
        </div>
      </div>
    </header>
  );
}
