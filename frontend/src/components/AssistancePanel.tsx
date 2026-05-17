import type { ScenarioInput } from "../types/flight";
import { ExplanationCard } from "./ExplanationCard";
import { ProvenanceBadge } from "./ProvenanceBadge";
import { RiskBadge } from "./RiskBadge";

interface AssistancePanelProps {
  scenario: ScenarioInput;
}

export function AssistancePanel({ scenario }: AssistancePanelProps) {
  const active = scenario.assistance_request;
  const readiness = !active ? "Not required" : scenario.assistance_equipment_confirmed ? "Confirmed" : "Incomplete";
  const localizationStatus = scenario.assistance_localization_status || "No assistance status was returned.";
  const recommendation = !active
    ? "No passenger assistance action is required for the current scenario."
    : scenario.assistance_equipment_confirmed
    ? "Maintain confirmation with the gate team and verify stand-side handoff timing."
    : "Pre-position wheelchair or assistance equipment and confirm readiness before arrival.";

  return (
    <section className="panel p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="muted-label">Passenger assistance</div>
          <h3 className="mt-2 panel-title">Assistance readiness status</h3>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <ProvenanceBadge
            provenance={{
              category: "rule_based_logic",
              label: "Rule-based logic",
              summary: "Passenger assistance support is implemented as dispatch-readiness logic rather than a trained localization model.",
            }}
          />
          <RiskBadge label={readiness} />
        </div>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-3">
        <ExplanationCard title="Request status" body={active ? "Active" : "Inactive"} />
        <ExplanationCard title="Localization / equipment status" body={localizationStatus} />
        <ExplanationCard
          title="Operator recommendation"
          body={recommendation}
          footnote="This module is intentionally presented as rule-based assistance-readiness support."
        />
      </div>
    </section>
  );
}
