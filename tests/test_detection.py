from guardian_ai.agent.detection import Detector
import numpy as np


def test_heuristic_detector_flags_burst():
    d = Detector(model_path=None, threshold=-0.15)
    x = np.array([0.1, 10.0, 3.0, 4.0, 8.0])
    flag, score = d.is_anomaly(x)
    assert flag is True
    assert score < -0.15
