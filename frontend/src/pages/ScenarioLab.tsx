import { startTransition, useDeferredValue, useEffect, useMemo, useState } from "react";

import { ActionQueue } from "../components/ActionQueue";
import { ExplanationCard } from "../components/ExplanationCard";
import { KPIWidgets } from "../components/KPIWidgets";
import { RiskBadge } from "../components/RiskBadge";
import { ScenarioControls } from "../components/ScenarioControls";
import { ScenarioPresetBar } from "../components/ScenarioPresetBar";
import { fallbackScenarioPresets } from "../data/demoScenarios";
import { defaultScenarioSeed, fetchDemoScenarios, recomputeScenario } from "../lib/api";
import { formatPercent } from "../lib/format";
import type { RecomputeResponse, ScenarioInput } from "../types/flight";

export function ScenarioLab() {
  const [scenario, setScenario] = useState<ScenarioInput>(fallbackScenarioPresets[0]?.scenario ?? defaultScenarioSeed);
  const [result, setResult] = useState<RecomputeResponse | null>(null);
  const [status, setStatus] = useState("Computing local scenario response.");
  const [presets, setPresets] = useState(fallbackScenarioPresets);
  const deferredScenario = useDeferredValue(scenario);

  useEffect(() => {
    let mounted = true;
    fetchDemoScenarios().then((response) => {
      if (!mounted) return;
      const resolved = response.scenarios.map((scenarioItem) => {
        const fallback = fallbackScenarioPresets.find((preset) => preset.id === scenarioItem.id);
        return {
          id: scenarioItem.id,
          name: fallback?.name ?? scenarioItem.flight_number,
          description: fallback?.description ?? scenarioItem.route,
          scenario: scenarioItem,
        };
      });
      setPresets(resolved);
    });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    let mounted = true;
    setStatus("Recomputing module outputs.");
    recomputeScenario(deferredScenario).then((response) => {
      if (!mounted) return;
      startTransition(() => {
        setResult(response);
        setStatus("Outputs updated.");
      });
    });
    return () => {
      mounted = false;
    };
  }, [deferredScenario]);

  const active = result;
  const activePresetId = useMemo(
    () => presets.find((preset) => preset.scenario.id === scenario.id)?.id,
    [presets, scenario.id],
  );
  const resetSelectedCase = () => {
    const selectedPreset = presets.find((preset) => preset.id === activePresetId);
    setScenario(selectedPreset?.scenario ?? defaultScenarioSeed);
  };

  return (
    <div className="space-y-4">
      <section className="panel p-5">
        <div className="muted-label">Scenario lab</div>
        <h2 className="mt-2 text-2xl font-semibold text-white">Live what-if exploration</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
          Change a small set of operational inputs and observe how the local modules and OCC action queue respond.
        </p>
      </section>

      <ScenarioPresetBar presets={presets} activePresetId={activePresetId} onSelect={setScenario} />

      <div className="grid gap-4 xl:grid-cols-[0.88fr_1.12fr]">
        <ScenarioControls scenario={scenario} onChange={setScenario} onReset={resetSelectedCase} />
        <div className="space-y-4">
          <ExplanationCard title="Scenario status" body={status} />
          {active ? (
            <KPIWidgets
              items={[
                { label: "Readiness score", value: active.fusion.readiness_score.toFixed(1) },
                { label: "Expected delay risk", value: `${active.fusion.expected_delay_risk_min.toFixed(1)} min` },
                { label: "Proactive benefit", value: `${active.fusion.expected_benefit_min.toFixed(1)} min`, note: "Simulated operator-facing indicator" },
              ]}
            />
          ) : null}
        </div>
      </div>

      {active ? (
        <>
          <section className="panel p-5">
            <div className="muted-label">Module response snapshot</div>
            <h3 className="mt-2 panel-title">What changed in the local decision-support chain</h3>
            <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <div className="rounded-2xl border border-panelEdge/80 bg-slate-950/35 p-4">
                <div className="muted-label">Maintenance</div>
                <div className="mt-3 flex items-center gap-2">
                  <RiskBadge label={active.maintenance.urgency_class} />
                  <span className="text-sm text-slate-300">{formatPercent(active.maintenance.failure_probability)}</span>
                </div>
              </div>
              <div className="rounded-2xl border border-panelEdge/80 bg-slate-950/35 p-4">
                <div className="muted-label">Inventory</div>
                <div className="mt-3 flex items-center gap-2">
                  <RiskBadge label={active.inventory.risk_level} />
                  <span className="text-sm text-slate-300">{formatPercent(active.inventory.shortage_risk)}</span>
                </div>
              </div>
              <div className="rounded-2xl border border-panelEdge/80 bg-slate-950/35 p-4">
                <div className="muted-label">Assistance</div>
                <div className="mt-3">
                  <RiskBadge
                    label={
                      !active.scenario.assistance_request
                        ? "Not required"
                        : active.scenario.assistance_equipment_confirmed
                          ? "Confirmed"
                          : "Incomplete"
                    }
                  />
                </div>
              </div>
              <div className="rounded-2xl border border-panelEdge/80 bg-slate-950/35 p-4">
                <div className="muted-label">Bottleneck</div>
                <div className="mt-3">
                  <RiskBadge label={active.bottleneck.dominant_bottleneck} tone="info" />
                </div>
              </div>
            </div>
          </section>
          <ActionQueue actions={active.fusion.action_queue} maxItems={3} />
        </>
      ) : null}
    </div>
  );
}
