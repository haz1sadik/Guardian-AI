from __future__ import annotations

import argparse
import pandas as pd
from joblib import load
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

FEATURES = ["created_rate", "modified_rate", "deleted_rate", "renamed_rate", "distinct_ext"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Guardian-AI Isolation Forest")
    parser.add_argument("--model", required=True)
    parser.add_argument("--input", required=True, help="CSV with feature columns + label (0 benign, 1 attack)")
    parser.add_argument("--label-col", default="label")
    parser.add_argument("--threshold", type=float, default=-0.15)
    args = parser.parse_args()

    model = load(args.model)
    df = pd.read_csv(args.input)
    X = df[FEATURES]
    y = df[args.label_col].astype(int)

    scores = model.decision_function(X)
    y_pred = (scores < args.threshold).astype(int)

    print("Confusion Matrix:")
    print(confusion_matrix(y, y_pred))
    print("\nClassification Report:")
    print(classification_report(y, y_pred, digits=4))
    try:
        print(f"ROC-AUC (score inversion): {roc_auc_score(y, -scores):.4f}")
    except Exception:
        pass


if __name__ == "__main__":
    main()
