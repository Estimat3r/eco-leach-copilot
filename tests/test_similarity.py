"""Unit tests for src/engine/similarity.py."""

import numpy as np
import pandas as pd

from src.data.loader import load_dataset
from src.engine.similarity import compute_distances, find_nearest_k


def test_compute_distances_shape():
    df = load_dataset()
    condition = {"temp_C": 50.0, "time_min": 60.0, "h2so4_M": 1.0, "h2o2_M": 0.5, "pulp_density_gL": 100.0}
    distances = compute_distances(condition, df)
    assert distances.shape == (len(df),)
    assert np.all(distances >= 0)


def test_find_nearest_k_returns_k():
    df = load_dataset()
    condition = {"temp_C": 50.0, "time_min": 60.0, "h2so4_M": 1.0, "h2o2_M": 0.5, "pulp_density_gL": 100.0}
    distances = compute_distances(condition, df)
    indices, dists = find_nearest_k(distances, k=5)
    assert len(indices) == 5
    assert len(dists) == 5
    # 거리 순 정렬 확인
    assert np.all(np.diff(dists) >= 0)


def test_exact_match_distance_zero():
    """데이터셋의 첫 행을 입력하면 거리 0."""
    df = load_dataset()
    row = df.iloc[0]
    condition = {col: float(row[col]) for col in ["temp_C", "time_min", "h2so4_M", "h2o2_M", "pulp_density_gL"]}
    distances = compute_distances(condition, df)
    assert distances[0] < 1e-10
