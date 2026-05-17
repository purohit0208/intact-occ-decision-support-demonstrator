const safeNumber = (value: number, fallback = 0) => (Number.isFinite(value) ? value : fallback);

export const formatPercent = (value: number) => `${Math.round(safeNumber(value) * 100)}%`;
export const formatScore = (value: number) => `${safeNumber(value).toFixed(1)}`;
export const formatDelay = (minutes: number) => `${Math.round(safeNumber(minutes))} min`;
export const formatMaintenanceStatus = (value: string) => {
  const normalized = value.trim().toUpperCase();
  if (normalized === "OK") return "LOW";
  if (normalized === "PLAN") return "ELEVATED";
  if (normalized === "SOON") return "HIGH";
  return value;
};
export const titleCaseWords = (value: string) =>
  value
    .split(/[_\s]+/)
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
