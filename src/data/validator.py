"""입력값 검증 및 범위 검사."""

import pandas as pd

from src.data.schema import INPUT_COLUMNS
from src.models import SupportedRange, ValidationResult


def compute_supported_ranges(df: pd.DataFrame) -> dict[str, SupportedRange]:
    """데이터셋에서 각 입력 변수의 min/max 범위를 계산."""
    ranges: dict[str, SupportedRange] = {}
    for col in INPUT_COLUMNS:
        ranges[col] = SupportedRange(
            min_val=float(df[col].min()),
            max_val=float(df[col].max()),
        )
    return ranges


def validate_input(
    inputs: dict[str, float],
    supported_ranges: dict[str, SupportedRange],
) -> ValidationResult:
    """입력값의 타입, 음수, 범위를 검증."""
    warnings: list[str] = []
    errors: list[str] = []

    for name in INPUT_COLUMNS:
        value = inputs.get(name)

        # 숫자 타입 검증
        if value is None or not isinstance(value, (int, float)):
            errors.append(f"{name}: 숫자 값을 입력해주세요")
            continue

        # 음수 거부
        if value < 0:
            errors.append(f"{name}: 음수 값은 허용되지 않습니다")
            continue

        # Supported Range 범위 검사
        if name in supported_ranges:
            sr = supported_ranges[name]
            if value < sr.min_val or value > sr.max_val:
                warnings.append(
                    f"{name} ({value})이 지원 범위({sr.min_val}~{sr.max_val})를 벗어납니다"
                )

    is_valid = len(errors) == 0
    return ValidationResult(is_valid=is_valid, warnings=warnings, errors=errors)
