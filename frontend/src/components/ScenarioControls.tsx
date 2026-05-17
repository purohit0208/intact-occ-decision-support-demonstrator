import type { ScenarioInput } from "../types/flight";

interface ScenarioControlsProps {
  scenario: ScenarioInput;
  onChange: (scenario: ScenarioInput) => void;
  onReset: () => void;
}

interface SliderFieldProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  suffix?: string;
  onChange: (value: number) => void;
}

function SliderField({ label, value, min, max, step = 1, suffix = "", onChange }: SliderFieldProps) {
  return (
    <label className="block rounded-2xl border border-panelEdge/80 bg-slate-950/35 p-4">
      <div className="flex items-center justify-between gap-3">
        <span className="text-sm font-medium text-slate-200">{label}</span>
        <span className="text-sm font-semibold text-white">
          {value}
          {suffix}
        </span>
      </div>
      <input
        className="mt-4 h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-800 accent-cyan-400"
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}

export function ScenarioControls({ scenario, onChange, onReset }: ScenarioControlsProps) {
  const patch = <K extends keyof ScenarioInput>(key: K, value: ScenarioInput[K]) => onChange({ ...scenario, [key]: value });
  const toggleAssistanceRequest = () =>
    onChange({
      ...scenario,
      assistance_request: !scenario.assistance_request,
      assistance_equipment_confirmed: scenario.assistance_request ? false : scenario.assistance_equipment_confirmed,
    });

  return (
    <section className="panel p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="muted-label">Scenario controls</div>
          <h3 className="mt-2 panel-title">What-if input layer</h3>
        </div>
        <button
          type="button"
          onClick={onReset}
          className="rounded-full border border-panelEdge px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-200 transition hover:border-signal.cyan/50 hover:text-white"
        >
          Reset selected case
        </button>
      </div>

      <div className="mt-5 grid gap-3 xl:grid-cols-2">
        <SliderField label="Passenger load" value={scenario.passenger_load} min={60} max={220} onChange={(value) => patch("passenger_load", value)} />
        <SliderField label="Arrival delay" value={scenario.arrival_delay} min={0} max={90} suffix=" min" onChange={(value) => patch("arrival_delay", value)} />
        <SliderField label="Malfunction count" value={scenario.malfunction_count} min={0} max={6} onChange={(value) => patch("malfunction_count", value)} />
        <SliderField label="Malfunction severity" value={scenario.malfunction_severity} min={0} max={10} step={0.1} onChange={(value) => patch("malfunction_severity", value)} />
        <SliderField label="Inventory shortage" value={scenario.inventory_shortage_score} min={0} max={10} step={0.1} onChange={(value) => patch("inventory_shortage_score", value)} />
        <SliderField label="Gate congestion" value={scenario.gate_congestion} min={0} max={10} step={0.1} onChange={(value) => patch("gate_congestion", value)} />
        <SliderField label="Weather disturbance" value={scenario.weather_disturbance} min={0} max={10} step={0.1} onChange={(value) => patch("weather_disturbance", value)} />
        <SliderField
          label="Trolley availability"
          value={Math.round(scenario.trolley_availability * 100)}
          min={10}
          max={100}
          suffix="%"
          onChange={(value) => patch("trolley_availability", value / 100)}
        />
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <button
          type="button"
          onClick={toggleAssistanceRequest}
          className={`rounded-2xl border px-4 py-4 text-left transition ${
            scenario.assistance_request
              ? "border-signal.coral/40 bg-signal.coral/10 text-white"
              : "border-panelEdge bg-slate-950/35 text-slate-300"
          }`}
        >
          <div className="text-sm font-semibold">Passenger assistance request</div>
          <div className="mt-2 text-xs uppercase tracking-[0.18em]">{scenario.assistance_request ? "Active" : "Inactive"}</div>
        </button>
        <button
          type="button"
          onClick={() => patch("assistance_equipment_confirmed", !scenario.assistance_equipment_confirmed)}
          disabled={!scenario.assistance_request}
          className={`rounded-2xl border px-4 py-4 text-left transition ${
            scenario.assistance_equipment_confirmed
              ? "border-emerald-500/40 bg-emerald-500/10 text-white"
              : "border-panelEdge bg-slate-950/35 text-slate-300"
          } ${!scenario.assistance_request ? "cursor-not-allowed opacity-50" : ""}`}
        >
          <div className="text-sm font-semibold">Assistance equipment confirmed</div>
          <div className="mt-2 text-xs uppercase tracking-[0.18em]">
            {scenario.assistance_equipment_confirmed ? "Confirmed" : "Unconfirmed"}
          </div>
        </button>
      </div>
    </section>
  );
}
