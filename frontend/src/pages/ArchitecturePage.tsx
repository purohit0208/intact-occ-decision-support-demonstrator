import { architectureLayers } from "../data/demoConfig";
import { ExplanationCard } from "../components/ExplanationCard";

export function ArchitecturePage() {
  return (
    <div className="space-y-4">
      <section className="panel p-5">
        <div className="muted-label">Architecture / about</div>
        <h2 className="mt-2 text-2xl font-semibold text-white">Compact system view</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
          This page gives only the demonstrator-level architecture. Detailed evaluation tables, limitations, and model
          development evidence are better discussed in the accompanying presentation or paper.
        </p>
      </section>

      <section className="panel p-5">
        <div className="muted-label">Operational concept</div>
        <h3 className="mt-2 panel-title">Four-layer local decision-support flow</h3>
        <div className="mt-5 grid gap-4 xl:grid-cols-4">
          {architectureLayers.map((layer, index) => (
            <div key={layer.title} className="relative rounded-3xl border border-panelEdge/80 bg-slate-950/35 p-5">
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-signal.cyan">Layer {index + 1}</div>
              <div className="mt-3 text-lg font-semibold text-white">{layer.title}</div>
              <p className="mt-3 text-sm leading-6 text-slate-300">{layer.body}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="grid gap-4 xl:grid-cols-3">
        <ExplanationCard
          title="Human-in-the-loop"
          body="The system recommends coordination actions; it does not automate dispatch or operational control."
        />
        <ExplanationCard
          title="Local inference"
          body="Maintenance, inventory, and bottleneck modules run from saved local model artifacts."
        />
        <ExplanationCard
          title="Simulated boundary"
          body="Scenario inputs and impact indicators are synthetic and are not airline deployment evidence."
        />
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <ExplanationCard
          title="Readiness score"
          body="Formula: 100 minus maintenance status, failure risk, inventory risk, bottleneck pressure, congestion, delay, assistance gap, and cross-domain compounding penalties. Routine > 74; Watch 57-74; Priority 39-56; Critical <= 38."
        />
        <ExplanationCard
          title="Maintenance labels"
          body="LOW: routine monitoring. ELEVATED: diagnostic review. HIGH: inspection and spare preparation. CRITICAL: technician dispatch. Synthetic target thresholds use failure probability and remaining-flight proxy."
        />
        <ExplanationCard
          title="Inventory labels"
          body="LOW: shortage risk below 45%. ELEVATED: 45-74%. HIGH: 75% or above. The displayed risk combines the trained inventory classifier with a transparent monotonic what-if guard."
        />
      </div>
    </div>
  );
}
