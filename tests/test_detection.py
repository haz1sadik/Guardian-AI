from guardian_ai.agent.detection import Detector
import numpy as np
from sklearn.ensemble import IsolationForest
from joblib import dump


def test_heuristic_detector_flags_burst():
    d = Detector(model_path=None, threshold=-0.15)
    x = np.array([0.1, 10.0, 3.0, 4.0, 8.0])
    flag, score = d.is_anomaly(x)
    assert flag is True
    assert score < -0.15


def test_model_detector_path_loads_and_scores(tmp_path):
    X = np.array(
        [
            [0.1, 0.2, 0.0, 0.0, 1.0],
            [0.2, 0.3, 0.0, 0.0, 1.0],
            [0.15, 0.25, 0.0, 0.0, 1.0],
        ]
    )
    model = IsolationForest(random_state=42, contamination=0.1)
    model.fit(X)
    model_path = tmp_path / "if.joblib"
    dump(model, model_path)

    d = Detector(model_path=model_path, threshold=-0.15)
    flag, score = d.is_anomaly(np.array([5.0, 10.0, 3.0, 4.0, 8.0]))
    assert isinstance(flag, bool)
    assert isinstance(score, float)
