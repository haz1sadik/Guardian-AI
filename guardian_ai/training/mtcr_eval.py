from __future__ import annotations

import argparse
import csv
from statistics import mean


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute MTCR metrics from experiment log")
    parser.add_argument("--input", required=True, help="CSV with detect_ts, restore_done_ts in seconds")
    args = parser.parse_args()

    mtcr_values: list[float] = []
    with open(args.input, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mtcr_values.append(float(row["restore_done_ts"]) - float(row["detect_ts"]))

    if not mtcr_values:
        print("No rows")
        return

    print(f"runs={len(mtcr_values)}")
    print(f"mtcr_mean={mean(mtcr_values):.3f}s")
    print(f"mtcr_min={min(mtcr_values):.3f}s")
    print(f"mtcr_max={max(mtcr_values):.3f}s")


if __name__ == "__main__":
    main()
