import type { ProvenanceInfo } from "../types/provenance";

interface ProvenanceBadgeProps {
  provenance: ProvenanceInfo;
}

export function ProvenanceBadge({ provenance }: ProvenanceBadgeProps) {
  const classes =
    provenance.category === "trained_ml_inference"
      ? "border-emerald-400/25 bg-emerald-400/10 text-emerald-200"
      : provenance.category === "rule_based_logic"
        ? "border-amber-400/25 bg-amber-400/10 text-amber-100"
        : provenance.category === "fallback_placeholder"
          ? "border-rose-400/25 bg-rose-400/10 text-rose-100"
          : "border-slate-400/25 bg-slate-400/10 text-slate-200";

  return (
    <div className={`inline-flex rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] ${classes}`}>
      {provenance.label}
    </div>
  );
}
