"""유클리드 거리 기반 nearest-condition search."""

import numpy as np
import pandas as pd

from src.data.schema import INPUT_COLUMNS

DEFAULT_WEIGHTS = {
    "temp_C": 1.0,
    "time_min": 0.8,
    "h2so4_M": 1.0,
    "h2o2_M": 0.8,
    "pulp_density_gL": 0.6,
}


def compute_distances(
    input_condition: dict[str, float],
    dataset: pd.DataFrame,
    weights: dict[str, float] | None = None,
) -> np.ndarray:
    """입력 조건과 데이터셋 전체 행 간의 정규화된 가중 유클리드 거리 배열 반환."""
    if weights is None:
        weights = DEFAULT_WEIGHTS

    squared_sum = np.zeros(len(dataset))

    for col in INPUT_COLUMNS:
        col_min = dataset[col].min()
        col_max = dataset[col].max()
        col_range = col_max - col_min
        if col_range == 0:
            continue

        w = weights.get(col, 1.0)
        diff = (input_condition[col] - dataset[col].values) / col_range
        squared_sum += w * (diff ** 2)

    return np.sqrt(squared_sum)


def find_nearest_k(
    distances: np.ndarray,
    k: int = 5,
) -> tuple[np.ndarray, np.ndarray]:
    """가장 가까운 k개 인덱스와 거리 반환."""
    k = min(k, len(distances))
    indices = np.argpartition(distances, k)[:k]
    # 거리 순 정렬
    sorted_order = np.argsort(distances[indices])
    indices = indices[sorted_order]
    return indices, distances[indices]
