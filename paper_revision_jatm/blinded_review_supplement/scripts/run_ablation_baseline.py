from __future__ import annotations

from jatm_eval_core import OUTPUT_TABLES, run_ablation_baseline


def main() -> None:
    ablation_summary, action_shift, baseline = run_ablation_baseline()
    print(f"Wrote ablation and baseline outputs under {OUTPUT_TABLES}.")
    print(f"Ablation configurations: {len(ablation_summary)}")
    print(f"Action-shift rows: {len(action_shift)}")
    print(f"Baselines: {len(baseline)}")


if __name__ == "__main__":
    main()
