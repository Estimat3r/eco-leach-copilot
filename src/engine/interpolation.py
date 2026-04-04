"""Inverse-distance weighted interpolation."""

import numpy as np
import pandas as pd

EPSILON = 1e-8


def weighted_interpolation(
    nearest_rows: pd.DataFrame,
    distances: np.ndarray,
    output_columns: list[str],
) -> dict[str, float]:
    """inverse-distance weighted average로 금속별 침출률 계산.

    w_i = 1 / (d_i + EPSILON)
    result_metal = sum(w_i * value_i) / sum(w_i)
    결과는 0~100% 범위로 클리핑.
    """
    weights = 1.0 / (distances + EPSILON)
    total_weight = weights.sum()

    result: dict[str, float] = {}
    for col in output_columns:
        values = nearest_rows[col].values
        weighted_avg = float(np.sum(weights * values) / total_weight)
        result[col] = float(np.clip(weighted_avg, 0.0, 100.0))

    return result
