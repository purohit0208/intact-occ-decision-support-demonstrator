import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ChevronLeft } from "lucide-react";

import { ActionQueue } from "../components/ActionQueue";
import { AssistancePanel } from "../components/AssistancePanel";
import { BottleneckPanel } from "../components/BottleneckPanel";
import { ExplanationCard } from "../components/ExplanationCard";
import { ExportBriefButton } from "../components/ExportBriefButton";
import { InventoryPanel } from "../components/InventoryPanel";
import { MaintenancePanel } from "../components/MaintenancePanel";
import { ProvenanceBadge } from "../components/ProvenanceBadge";
import { ReadinessBreakdown } from "../components/ReadinessBreakdown";
import { RiskBadge } from "../components/RiskBadge";
import { fetchFlightDetail } from "../lib/api";
import { formatDelay, formatScore } from "../lib/format";
import type { FlightDetailResponse } from "../types/flight";

export function FlightDetail() {
  const { flightId = "" } = useParams();
  const navigate = useNavigate();
  const [detail, setDetail] = useState<FlightDetailResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    fetchFlightDetail(flightId)
      .then((response) => {
        if (mounted) {
          setDetail(response);
          setError(null);
        }
      })
      .catch(() => {
        if (mounted) {
          setError("Flight detail is unavailable until the backend is running.");
        }
      });
    return () => {
      mounted = false;
    };
  }, [flightId]);

  if (!detail) {
    return (
      <div className="panel p-6">
        <button type="button" onClick={() => navigate("/")} className="mb-4 inline-flex items-center gap-2 text-sm text-slate-300">
          <ChevronLeft className="h-4 w-4" />
          Back to dashboard
        </button>
        <div className="text-lg font-semibold text-white">{error ?? "Loading flight detail."}</div>
      </div>
    );
  }

  const { scenario, maintenance, inventory, bottleneck, fusion } = detail;
  const componentList = scenario.reported_components.length
    ? scenario.reported_components.join(", ")
    : "No component list was provided in the current scenario.";
  const cabinNotes = scenario.cabin_report_notes.length
    ? scenario.cabin_report_notes
    : ["No additional cabin-side notes were returned for this scenario."];

  return (
    <div className="space-y-4">
      <section className="panel p-5">
        <button type="button" onClick={() => navigate("/")} className="inline-flex items-center gap-2 text-sm text-slate-300 hover:text-white">
          <ChevronLeft className="h-4 w-4" />
          Back to dashboard
        </button>
        <div className="mt-4 grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
          <div>
            <div className="muted-label">Flight detail</div>
            <h2 className="mt-2 text-3xl font-semibold text-white">
              {scenario.flight_number} | {scenario.aircraft_type}
            </h2>
            <p className="mt-2 text-sm text-slate-300">{scenario.route}</p>
            <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <ExplanationCard title="ETA / Gate" body={`${scenario.eta} | ${scenario.gate}`} />
              <ExplanationCard title="Passenger load" body={String(scenario.passenger_load)} />
              <ExplanationCard title="Arrival delay" body={formatDelay(scenario.arrival_delay)} />
              <ExplanationCard title="Gate congestion" body={formatScore(scenario.gate_congestion)} />
            </div>
          </div>
          <div className="rounded-3xl border border-panelEdge/80 bg-slate-950/35 p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="muted-label">Fused readiness state</div>
              </div>
              <ExportBriefButton detail={detail} />
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <ProvenanceBadge provenance={fusion.provenance} />
              <RiskBadge label={fusion.alert_level} />
              <RiskBadge label={bottleneck.dominant_bottleneck} tone="info" />
            </div>
            <div className="mt-5 grid grid-cols-2 gap-4">
              <div>
                <div className="muted-label">Readiness score</div>
                <div className="mt-2 text-3xl font-semibold text-white">{formatScore(fusion.readiness_score)}</div>
              </div>
              <div>
                <div className="muted-label">Criticality score</div>
                <div className="mt-2 text-3xl font-semibold text-white">{formatScore(fusion.criticality_score)}</div>
              </div>
            </div>
            <p className="mt-4 text-sm leading-6 text-slate-300">
              Decision-support summary for operator review. No autonomous dispatch action is triggered.
            </p>
          </div>
        </div>
      </section>

      <section className="panel p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="muted-label">Aircraft-side / cabin report panel</div>
          <ProvenanceBadge
            provenance={{
              category: "scenario_simulation",
              label: "Scenario simulation",
              summary: "Aircraft-side structured messages are simulated but operationally grounded inputs used to drive local recomputation.",
            }}
          />
        </div>
        <h3 className="mt-2 panel-title">Pre-arrival structured information</h3>
        <div className="mt-5 grid gap-4 lg:grid-cols-3">
          <ExplanationCard
            title="Cabin discrepancy summary"
            body={`Reported malfunction count: ${scenario.malfunction_count}. Reported severity: ${formatScore(scenario.malfunction_severity)}.`}
          />
          <ExplanationCard
            title="Example component list"
            body={componentList}
            footnote="Structured aircraft-side messages are assumed to be available before landing in this demonstrator."
          />
          <ExplanationCard
            title="Assistance and inventory signals"
            body={`Assistance request: ${scenario.assistance_request ? "active" : "inactive"}. Inventory / trolley issue flag: ${scenario.inventory_shortage_score >= 4 ? "elevated" : "low"}.`}
          />
        </div>
        <p className="mt-4 text-sm leading-6 text-slate-400">{cabinNotes[0]}</p>
      </section>

      <MaintenancePanel maintenance={maintenance} />
      <InventoryPanel inventory={inventory} />
      <AssistancePanel scenario={scenario} />
      <BottleneckPanel bottleneck={bottleneck} />

      <div className="grid gap-4 xl:grid-cols-[1.05fr_0.95fr]">
        <ActionQueue actions={fusion.action_queue} maxItems={4} />
        <div className="space-y-4">
          <ExplanationCard title="Alert summary" body={fusion.alert_summary.join(" ")} />
          <ExplanationCard
            title="Estimated delay-risk indication"
            body={`${fusion.expected_delay_risk_min.toFixed(1)} simulated minutes of delay exposure under the current synthetic scenario.`}
            footnote={`Estimated benefit of proactive action: ${fusion.expected_benefit_min.toFixed(1)} minutes.`}
          />
        </div>
      </div>

      <ReadinessBreakdown factors={fusion.readiness_breakdown} maxItems={4} />
    </div>
  );
}
