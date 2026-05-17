export type PriorityLevel = "P1" | "P2" | "P3" | "P4";

export interface ActionItem {
  priority: PriorityLevel;
  team: string;
  description: string;
  rationale: string;
  expected_impact: string;
}
