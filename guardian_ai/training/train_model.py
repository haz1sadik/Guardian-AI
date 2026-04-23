from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
from sklearn.ensemble import IsolationForest
from joblib import dump
from guardian_ai.common.constants import FEATURES


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Isolation Forest for Guardian-AI MVP")
    parser.add_argument("--input", required=True, help="CSV of BENIGN baseline windows")
    parser.add_argument("--output", required=True, help="Output model .joblib path")
    parser.add_argument("--contamination", type=float, default=0.08)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    X = df[FEATURES]

    model = IsolationForest(
        n_estimators=200,
        contamination=args.contamination,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    dump(model, out)
    print(f"saved model -> {out}")


if __name__ == "__main__":
    main()
