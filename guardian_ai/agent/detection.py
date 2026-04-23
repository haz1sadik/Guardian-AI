from __future__ import annotations

from pathlib import Path
from sklearn.ensemble import IsolationForest
from joblib import load
import numpy as np
import time

# Feature index mapping for vectors ordered as guardian_ai.common.constants.FEATURES.
IDX_CREATED_RATE = 0
IDX_MODIFIED_RATE = 1
IDX_DELETED_RATE = 2
IDX_RENAMED_RATE = 3
IDX_DISTINCT_EXT = 4


class FeatureWindow:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.start = time.perf_counter()
        self.created = 0
        self.modified = 0
        self.deleted = 0
        self.renamed = 0
        self.extensions: set[str] = set()

    def add_event(self, event_type: str, path: str) -> None:
        if event_type == "created":
            self.created += 1
        elif event_type == "modified":
            self.modified += 1
        elif event_type == "deleted":
            self.deleted += 1
        elif event_type == "moved":
            self.renamed += 1
        self.extensions.add(Path(path).suffix.lower())

    def vector(self) -> np.ndarray:
        elapsed = max(1.0, time.perf_counter() - self.start)
        return np.array([
            self.created / elapsed,
            self.modified / elapsed,
            self.deleted / elapsed,
            self.renamed / elapsed,
            float(len(self.extensions)),
        ], dtype=float)


class Detector:
    def __init__(self, model_path: Path | None, threshold: float = -0.15) -> None:
        self.threshold = threshold
        self.model = None
        if model_path and model_path.exists():
            self.model = load(model_path)

    def _heuristic_score(self, x: np.ndarray) -> float:
        created_rate = float(x[IDX_CREATED_RATE])
        modified_rate = float(x[IDX_MODIFIED_RATE])
        deleted_rate = float(x[IDX_DELETED_RATE])
        renamed_rate = float(x[IDX_RENAMED_RATE])
        ext_count = float(x[IDX_DISTINCT_EXT])
        return -(
            max(0.0, modified_rate - 2.0)
            + 1.2 * max(0.0, renamed_rate - 0.5)
            + 1.1 * max(0.0, deleted_rate - 0.2)
            + 0.8 * max(0.0, ext_count - 4.0)
            + 0.6 * max(0.0, created_rate - 2.0)
        )

    def score(self, x: np.ndarray) -> float:
        if self.model is not None and isinstance(self.model, IsolationForest):
            return float(self.model.decision_function([x])[0])
        return self._heuristic_score(x)

    def is_anomaly(self, x: np.ndarray) -> tuple[bool, float]:
        score = self.score(x)
        return (score < self.threshold), score
