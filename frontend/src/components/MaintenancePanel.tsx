import type { MaintenancePrediction } from "../types/maintenance";
import { formatPercent } from "../lib/format";
import { ExplanationCard } from "./ExplanationCard";
import { ProvenanceBadge } from "./ProvenanceBadge";
import { RiskBadge } from "./RiskBadge";

interface MaintenancePanelProps {
  maintenance: MaintenancePrediction;
}

export function MaintenancePanel({ maintenance }: MaintenancePanelProps) {
  const width = `${Math.round(maintenance.failure_probability * 100)}%`;
  const affectedComponents = maintenance.affected_components.length
    ? maintenance.affected_components.join(", ")
    : "No affected component list was returned.";

  return (
    <section className="panel p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="muted-label">Predictive maintenance intelligence</div>
          <h3 className="mt-2 panel-title">Cabin component condition</h3>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <ProvenanceBadge provenance={maintenance.provenance} />
          <RiskBadge label={maintenance.urgency_class} />
        </div>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-4">
          <div className="rounded-2xl border border-panelEdge/80 bg-slate-950/35 p-4">
            <div className="flex items-end justify-between">
              <div>
                <div className="muted-label">Failure probability</div>
                <div className="mt-2 text-3xl font-semibold text-white">{formatPercent(maintenance.failure_probability)}</div>
                <div className="mt-2 text-xs uppercase tracking-[0.16em] text-slate-400">
                  Confidence {formatPercent(maintenance.confidence)}
                </div>
              </div>
              <div className="text-right">
                <div className="muted-label">Remaining flights</div>
                <div className="mt-2 text-2xl font-semibold text-white">{maintenance.remaining_flights_estimate}</div>
              </div>
            </div>
            <div className="mt-4 h-3 rounded-full bg-slate-800">
              <div className="h-3 rounded-full bg-gradient-to-r from-signal.amber to-signal.coral" style={{ width }} />
            </div>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <ExplanationCard title="Affected components" body={affectedComponents} />
            <ExplanationCard
              title="Recommended maintenance action"
              body={maintenance.recommended_action}
              footnote={`${maintenance.provenance.selected_model || maintenance.model_source}${maintenance.provenance.development_metric ? ` | ${maintenance.provenance.development_metric}` : ""}${maintenance.provenance.test_metric ? ` | ${maintenance.provenance.test_metric}` : ""}`}
            />
          </div>
        </div>
        <ExplanationCard
          title="Interpretation"
          body={maintenance.explanation}
          footnote={maintenance.anomaly_flag ? "Anomaly flag active." : "No anomaly flag active."}
        />
      </div>
    </section>
  );
}
