from __future__ import annotations

from jatm_eval_core import OUTPUT_TABLES, run_monotonicity_checks


def main() -> None:
    detail, summary = run_monotonicity_checks()
    passed = int(summary["passed"].sum())
    print(f"Wrote monotonicity outputs under {OUTPUT_TABLES}. Passed {passed}/{len(summary)} checks.")


if __name__ == "__main__":
    main()
