"""Unit tests for src/engine/interpolation.py."""

import numpy as np
import pandas as pd

from src.engine.interpolation import weighted_interpolation, EPSILON


def test_weighted_interpolation_basic():
    """기본 weighted interpolation 계산."""
    data = pd.DataFrame({"Li_pct": [80.0, 90.0], "Ni_pct": [70.0, 80.0]})
    distances = np.array([0.1, 0.2])
    result = weighted_interpolation(data, distances, ["Li_pct", "Ni_pct"])
    # 가까운 쪽에 더 가중치
    assert 80.0 < result["Li_pct"] < 90.0
    assert 70.0 < result["Ni_pct"] < 80.0


def test_weighted_interpolation_clipping():
    """결과가 0~100 범위로 클리핑."""
    data = pd.DataFrame({"Li_pct": [105.0, 110.0]})
    distances = np.array([0.1, 0.2])
    result = weighted_interpolation(data, distances, ["Li_pct"])
    assert result["Li_pct"] == 100.0


def test_equal_distances():
    """동일 거리면 단순 평균."""
    data = pd.DataFrame({"Li_pct": [60.0, 80.0]})
    distances = np.array([0.1, 0.1])
    result = weighted_interpolation(data, distances, ["Li_pct"])
    assert abs(result["Li_pct"] - 70.0) < 0.01
