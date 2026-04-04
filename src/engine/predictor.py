"""예측 엔진 메인: 모드 선택 + 결과 조합."""

import pandas as pd

from src.data.schema import OUTPUT_COLUMNS
from src.engine.confidence import compute_confidence_tier
from src.engine.interpolation import weighted_interpolation
from src.engine.similarity import compute_distances, find_nearest_k
from src.models import PredictionResult

THRESHOLD_EXACT = 0.1
THRESHOLD_INTERPOLATION = 0.3


def predict(
    input_condition: dict[str, float],
    dataset: pd.DataFrame,
) -> PredictionResult:
    """입력 조건에 대한 금속별 침출률 예측 수행.

    1. 거리 계산
    2. 모드 선택 (exact / interpolation / extrapolation)
    3. 침출률 계산
    4. confidence tier 결정
    5. 결과 조합 반환
    """
    distances = compute_distances(input_condition, dataset)
    nearest_idx, nearest_dist = find_nearest_k(distances, k=5)

    min_distance = float(nearest_dist[0])
    warnings: list[str] = []

    # 모드 선택 및 침출률 계산
    if min_distance < THRESHOLD_EXACT:
        # exact: 가장 가까운 포인트 직접 참조
        mode = "exact"
        row = dataset.iloc[nearest_idx[0]]
        leach_rates = {col: float(row[col]) for col in OUTPUT_COLUMNS}
    elif min_distance <= THRESHOLD_INTERPOLATION:
        # interpolation: k=3~5 weighted average
        k = max(3, min(5, len(nearest_idx)))
        idx = nearest_idx[:k]
        dist = nearest_dist[:k]
        mode = "interpolation"
        leach_rates = weighted_interpolation(
            dataset.iloc[idx], dist, OUTPUT_COLUMNS
        )
    else:
        # extrapolation: 경고와 함께 결과 반환
        mode = "extrapolation"
        warnings.append("지원 범위 밖 예측입니다. 결과의 신뢰도가 낮습니다")
        k = max(3, min(5, len(nearest_idx)))
        idx = nearest_idx[:k]
        dist = nearest_dist[:k]
        leach_rates = weighted_interpolation(
            dataset.iloc[idx], dist, OUTPUT_COLUMNS
        )

    # 0~100 클리핑
    for metal in leach_rates:
        leach_rates[metal] = max(0.0, min(100.0, leach_rates[metal]))

    # confidence tier
    num_within = int((nearest_dist <= THRESHOLD_INTERPOLATION).sum())
    confidence = compute_confidence_tier(min_distance, num_within)

    return PredictionResult(
        leach_rates=leach_rates,
        confidence_tier=confidence,
        nearest_distance=min_distance,
        prediction_mode=mode,
        warnings=warnings,
    )
