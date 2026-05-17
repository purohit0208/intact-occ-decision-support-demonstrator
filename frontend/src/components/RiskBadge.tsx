import clsx from "clsx";
import { formatMaintenanceStatus } from "../lib/format";

type Tone = "neutral" | "good" | "warning" | "critical" | "info";

interface RiskBadgeProps {
  label: string;
  tone?: Tone;
}

const toneClasses: Record<Tone, string> = {
  neutral: "border-slate-600/80 bg-slate-800/80 text-slate-200",
  good: "border-emerald-500/30 bg-emerald-500/10 text-emerald-200",
  warning: "border-amber-400/30 bg-amber-400/10 text-amber-200",
  critical: "border-rose-500/30 bg-rose-500/10 text-rose-200",
  info: "border-cyan-400/30 bg-cyan-400/10 text-cyan-200",
};

function inferTone(label: string): Tone {
  const upper = formatMaintenanceStatus(label).toUpperCase();
  if (upper.includes("CRITICAL") || upper.includes("P1") || upper.includes("HIGH")) return "critical";
  if (upper.includes("SOON") || upper.includes("PRIORITY") || upper.includes("WATCH") || upper.includes("ELEVATED")) return "warning";
  if (upper.includes("OK") || upper.includes("LOW") || upper.includes("CONFIRMED") || upper.includes("ROUTINE")) return "good";
  if (upper.includes("MAINTENANCE") || upper.includes("BOARDING")) return "info";
  return "neutral";
}

export function RiskBadge({ label, tone }: RiskBadgeProps) {
  const resolved = tone ?? inferTone(label);
  const displayLabel = formatMaintenanceStatus(label);
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.18em]",
        toneClasses[resolved],
      )}
    >
      {displayLabel}
    </span>
  );
}
