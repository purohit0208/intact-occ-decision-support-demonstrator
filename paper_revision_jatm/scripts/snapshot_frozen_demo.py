from __future__ import annotations

import argparse
from pathlib import Path

from jatm_eval_core import SNAPSHOT_DIR, compare_snapshot, write_snapshot_manifest


BASELINE = SNAPSHOT_DIR / "frozen_demo_manifest_baseline.csv"
CURRENT = SNAPSHOT_DIR / "frozen_demo_manifest_current.csv"
COMPARISON = SNAPSHOT_DIR / "frozen_demo_manifest_comparison.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or compare a checksum manifest for the frozen OCC demo files.")
    parser.add_argument("--write-baseline", action="store_true", help="Write the baseline manifest.")
    parser.add_argument("--compare", action="store_true", help="Compare the current manifest against the baseline.")
    args = parser.parse_args()

    if args.write_baseline:
        df = write_snapshot_manifest(BASELINE)
        print(f"Wrote {BASELINE} with {len(df)} files.")
    if args.compare:
        if not BASELINE.exists():
            raise FileNotFoundError(f"Missing baseline manifest: {BASELINE}")
        diff = compare_snapshot(BASELINE, CURRENT, COMPARISON)
        print(f"Wrote {COMPARISON} with {len(diff)} changed files.")
        if len(diff):
            print(diff.to_string(index=False))
    if not args.write_baseline and not args.compare:
        df = write_snapshot_manifest(CURRENT)
        print(f"Wrote {CURRENT} with {len(df)} files.")


if __name__ == "__main__":
    main()
