import type { FlightDetailResponse } from "../types/flight";
import { buildBriefingCsv, downloadCsv } from "../lib/export";

interface ExportBriefButtonProps {
  detail: FlightDetailResponse;
}

export function ExportBriefButton({ detail }: ExportBriefButtonProps) {
  return (
    <button
      type="button"
      onClick={() =>
        downloadCsv(
          `${detail.scenario.flight_number.replace(/[^a-z0-9_-]/gi, "_")}_briefing_snapshot.csv`,
          buildBriefingCsv(detail),
        )
      }
      className="rounded-full border border-panelEdge px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-200 transition hover:border-signal.cyan/50 hover:text-white"
    >
      Export briefing CSV
    </button>
  );
}
