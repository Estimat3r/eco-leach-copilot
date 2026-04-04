"""Carbon Proxy Index 계산 및 정규화."""

import pandas as pd

from src.sustainability.resource_metrics import (
    compute_acid_burden,
    compute_h2o2_burden,
    compute_heating_burden,
)


def compute_carbon_proxy(
    temp_C: float,
    time_min: float,
    h2so4_M: float,
    h2o2_M: float,
) -> float:
    """heating + acid + h2o2 burden의 합산 (raw 값)."""
    return (
        compute_heating_burden(temp_C, time_min)
        + compute_acid_burden(h2so4_M)
        + compute_h2o2_burden(h2o2_M)
    )


def normalize_carbon_proxy(raw_value: float, dataset_max: float) -> float:
    """데이터셋 내 최댓값 기준 0~1 정규화."""
    if dataset_max <= 0:
        return 0.0
    return min(raw_value / dataset_max, 1.0)


def compute_dataset_max_carbon(dataset: pd.DataFrame) -> float:
    """데이터셋 전체에서 최대 carbon proxy 값 계산."""
    import numpy as np

    heating = np.maximum(dataset["temp_C"].values - 25, 0.0) * dataset["time_min"].values * 0.001
    acid = dataset["h2so4_M"].values * 0.5
    h2o2 = dataset["h2o2_M"].values * 0.3
    totals = heating + acid + h2o2
    return float(totals.max()) if len(totals) > 0 else 0.0
