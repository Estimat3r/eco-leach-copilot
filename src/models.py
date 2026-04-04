"""핵심 데이터 모델 정의."""

from dataclasses import dataclass, field


@dataclass
class ProcessCondition:
    """사용자가 입력하는 공정 조건."""

    temp_C: float          # 온도 (°C), 범위: 10~90
    time_min: float        # 반응 시간 (min), 범위: 1~360
    h2so4_M: float         # 황산 농도 (M), 범위: 0.3~2.0
    h2o2_M: float          # H2O2 농도 (M), 범위: 0.0~1.96
    pulp_density_gL: float # 고액비 (g/L), 범위: 20~333


@dataclass
class PredictionResult:
    """예측 엔진의 출력 결과."""

    leach_rates: dict[str, float]  # {"Li_pct": ..., "Ni_pct": ..., ...}
    confidence_tier: str           # "high" | "medium" | "low"
    nearest_distance: float        # 가장 가까운 데이터 포인트와의 거리
    prediction_mode: str           # "exact" | "interpolation" | "extrapolation"
    warnings: list[str] = field(default_factory=list)


@dataclass
class CarbonResult:
    """Carbon Proxy 계산 결과."""

    heating_burden: float  # 온도/시간 기반 부담
    acid_burden: float     # 황산 기반 부담
    h2o2_burden: float     # H2O2 기반 부담
    total_raw: float       # 합산 raw 값
    normalized: float      # 0~1 정규화 값


@dataclass
class ValidationResult:
    """입력 검증 결과."""

    is_valid: bool
    warnings: list[str] = field(default_factory=list)  # 범위 밖 경고
    errors: list[str] = field(default_factory=list)     # 치명적 오류


@dataclass
class SupportedRange:
    """데이터셋 기반 지원 범위."""

    min_val: float
    max_val: float
