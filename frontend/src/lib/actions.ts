import type { ActionItem, PriorityLevel } from "../types/actions";

const priorityRank: Record<PriorityLevel, number> = {
  P1: 0,
  P2: 1,
  P3: 2,
  P4: 3,
};

export const sortActions = (actions: ActionItem[]) =>
  [...actions].sort((left, right) => priorityRank[left.priority] - priorityRank[right.priority]);
