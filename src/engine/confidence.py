"""Confidence tier 산출 및 경고 생성."""

from src.models import SupportedRange

THRESHOLD_HIGH = 0.1
THRESHOLD_MEDIUM = 0.3
MIN_NEIGHBORS_MEDIUM = 3


def compute_confidence_tier(
    nearest_distance: float,
    num_neighbors_within_threshold: int,
) -> str:
    """confidence tier 산출: high / medium / low."""
    if nearest_distance < THRESHOLD_HIGH:
        return "high"
    if nearest_distance <= THRESHOLD_MEDIUM and num_neighbors_within_threshold >= MIN_NEIGHBORS_MEDIUM:
        return "medium"
    return "low"


def generate_warnings(
    input_condition: dict[str, float],
    supported_ranges: dict[str, SupportedRange],
    nearest_distance: float,
) -> list[str]:
    """범위 밖 경고, extrapolation 경고 등 생성."""
    warnings: list[str] = []

    # 범위 밖 경고
    for name, value in input_condition.items():
        if name in supported_ranges:
            sr = supported_ranges[name]
            if value < sr.min_val or value > sr.max_val:
                warnings.append(
                    f"{name} ({value})이 지원 범위({sr.min_val}~{sr.max_val})를 벗어납니다"
                )

    # extrapolation 경고
    if nearest_distance > THRESHOLD_MEDIUM:
        warnings.append("데이터가 부족한 영역입니다. 결과의 신뢰도가 낮습니다")

    return warnings
