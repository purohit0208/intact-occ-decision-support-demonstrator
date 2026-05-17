import type { InventoryPrediction } from "../types/inventory";
import { formatPercent } from "../lib/format";
import { ExplanationCard } from "./ExplanationCard";
import { ProvenanceBadge } from "./ProvenanceBadge";
import { RiskBadge } from "./RiskBadge";

interface InventoryPanelProps {
  inventory: InventoryPrediction;
}

export function InventoryPanel({ inventory }: InventoryPanelProps) {
  const area = inventory.affected_service_area || "No affected service area returned";

  return (
    <section className="panel p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="muted-label">Inventory intelligence</div>
          <h3 className="mt-2 panel-title">Trolley and service readiness</h3>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <ProvenanceBadge provenance={inventory.provenance} />
          <RiskBadge label={inventory.risk_level} />
        </div>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-3">
        <ExplanationCard
          title="Shortage risk"
          body={formatPercent(inventory.shortage_risk)}
          footnote={`Confidence: ${formatPercent(inventory.confidence)}.`}
        />
        <ExplanationCard title="Affected service area" body={area} footnote={`Trolley status: ${inventory.trolley_status}.`} />
        <ExplanationCard
          title="Recommendation"
          body={inventory.recommendation}
          footnote={`${inventory.provenance.selected_model || inventory.model_source}${inventory.provenance.development_metric ? ` | ${inventory.provenance.development_metric}` : ""}${inventory.provenance.test_metric ? ` | ${inventory.provenance.test_metric}` : ""}`}
        />
      </div>
      <div className="mt-4">
        <ExplanationCard title="Interpretation" body={inventory.explanation} />
      </div>
    </section>
  );
}
