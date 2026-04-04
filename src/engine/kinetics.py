"""Kinetics Engine: 시간축 침출률 계산 및 포화 구간 감지."""

import numpy as np
import pandas as pd

from src.data.schema import OUTPUT_COLUMNS
from src.engine.predictor import predict


def compute_kinetics(
    temp_C: float,
    h2so4_M: float,
    h2o2_M: float,
    pulp_density_gL: float,
    dataset: pd.DataFrame,
    time_points: list[float] | None = None,
) -> pd.DataFrame:
    """시간축에 따른 금속별 침출률 변화를 계산.

    Args:
        temp_C: 온도 (°C)
        h2so4_M: 황산 농도 (M)
        h2o2_M: H2O2 농도 (M)
        pulp_density_gL: 고액비 (g/L)
        dataset: 데이터셋 DataFrame
        time_points: 시간 포인트 리스트 (기본: 1~360분, 20개 포인트)

    Returns:
        DataFrame with columns: time_min, Li_pct, Ni_pct, Co_pct, Mn_pct
    """
    if time_points is None:
        time_points = [1, 5, 10, 15, 20, 30, 45, 60, 90, 120,
                       150, 180, 210, 240, 270, 300, 330, 360]

    rows = []
    for t in time_points:
        condition = {
            "temp_C": temp_C,
            "time_min": float(t),
            "h2so4_M": h2so4_M,
            "h2o2_M": h2o2_M,
            "pulp_density_gL": pulp_density_gL,
        }
        result = predict(condition, dataset)
        row = {"time_min": float(t)}
        row.update(result.leach_rates)
        rows.append(row)

    return pd.DataFrame(rows)


def detect_saturation(
    kinetics_df: pd.DataFrame,
    threshold_pct: float = 1.0,
) -> str | None:
    """침출률 증가가 둔화되는 포화 구간을 감지.

    Args:
        kinetics_df: compute_kinetics()의 결과 DataFrame
        threshold_pct: 포화 판정 기준 (시간 구간당 증가율 %)

    Returns:
        포화 구간 해석 텍스트 또는 None
    """
    if len(kinetics_df) < 3:
        return None

    saturation_metals = []
    for col in OUTPUT_COLUMNS:
        values = kinetics_df[col].values
        times = kinetics_df["time_min"].values

        # 후반부에서 증가율이 threshold 이하인 구간 찾기
        for i in range(len(values) - 1, 1, -1):
            delta = abs(values[i] - values[i - 1])
            if delta > threshold_pct:
                sat_time = times[i]
                saturation_metals.append((col, sat_time))
                break

    if not saturation_metals:
        return None

    metal_names = {"Li_pct": "Li", "Ni_pct": "Ni", "Co_pct": "Co", "Mn_pct": "Mn"}
    parts = []
    for col, t in saturation_metals:
        name = metal_names.get(col, col)
        parts.append(f"{name}: 약 {t:.0f}분")

    if parts:
        return (
            f"포화 구간 감지: {', '.join(parts)} 이후 침출률 증가가 둔화됩니다. "
            "추가 반응 시간은 탄소 부담만 증가시킬 수 있으므로, "
            "자원 효율을 고려한 최적 반응 시간을 검토하세요."
        )
    return None
