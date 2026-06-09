from __future__ import annotations

import argparse

from jatm_eval_core import OUTPUT_TABLES, run_scenario_sweep


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the JATM large-scale synthetic scenario sweep.")
    parser.add_argument("--scenarios", type=int, default=1000, help="Number of synthetic scenarios to generate.")
    parser.add_argument("--seed", type=int, default=20260608, help="Deterministic random seed.")
    args = parser.parse_args()

    inputs, outputs = run_scenario_sweep(count=args.scenarios, seed=args.seed)
    print(f"Wrote {len(inputs)} input scenarios and {len(outputs)} output rows under {OUTPUT_TABLES}.")


if __name__ == "__main__":
    main()
