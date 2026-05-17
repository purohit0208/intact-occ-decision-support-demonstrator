import type { ScenarioInput } from "../types/flight";
import type { ScenarioPreset } from "../data/demoScenarios";

interface ScenarioPresetBarProps {
  presets: ScenarioPreset[];
  activePresetId?: string;
  onSelect: (scenario: ScenarioInput) => void;
}

export function ScenarioPresetBar({ presets, activePresetId, onSelect }: ScenarioPresetBarProps) {
  const activePreset = presets.find((preset) => preset.id === activePresetId) ?? presets[0];

  return (
    <section className="panel p-5">
      <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr] xl:items-end">
        <div>
          <div className="muted-label">Selected synthetic case</div>
          <h3 className="mt-2 panel-title">Choose flight for what-if testing</h3>
          <select
            value={activePreset?.id ?? ""}
            onChange={(event) => {
              const selected = presets.find((preset) => preset.id === event.target.value);
              if (selected) onSelect(selected.scenario);
            }}
            className="mt-4 w-full rounded-2xl border border-panelEdge/80 bg-slate-950/80 px-4 py-3 text-sm font-semibold text-white outline-none transition focus:border-signal.cyan/60"
          >
            {presets.map((preset) => (
              <option key={preset.id} value={preset.id}>
                {preset.scenario.flight_number} - {preset.name}
              </option>
            ))}
          </select>
        </div>
        {activePreset ? (
          <div className="rounded-2xl border border-panelEdge/80 bg-slate-950/35 p-4">
            <div className="text-sm font-semibold text-white">
              {activePreset.scenario.flight_number} | {activePreset.scenario.aircraft_type} | {activePreset.scenario.route}
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-300">{activePreset.description}</p>
          </div>
        ) : null}
      </div>
    </section>
  );
}
