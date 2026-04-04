"""탄소 배출량 계산 엔진 (kg CO₂ per batch).

기존 carbon_proxy를 대체하여 실제 emission factor 기반으로 계산.
"""

from __future__ import annotations
from dataclasses import dataclass

from src.sustainability.resource_metrics import (
    compute_acid_emission,
    compute_h2o2_emission,
    compute_heating_emission,
)


@dataclass
class CarbonBreakdown:
    """탄소 배출 분해 결과."""
    heating_kg: float       # 가열 에너지 CO₂ (kg)
    acid_kg: float          # H₂SO₄ 생산 CO₂ (kg)
    h2o2_kg: float          # H₂O₂ 생산 CO₂ (kg)
    total_kg: float         # 총 CO₂ (kg)

    @property
    def heating_pct(self) -> float:
        return (self.heating_kg / self.total_kg * 100) if self.total_kg > 0 else 0

    @property
    def acid_pct(self) -> float:
        return (self.acid_kg / self.total_kg * 100) if self.total_kg > 0 else 0

    @property
    def h2o2_pct(self) -> float:
        return (self.h2o2_kg / self.total_kg * 100) if self.total_kg > 0 else 0


def compute_carbon_emission(
    temp_C: float,
    time_min: float,
    h2so4_M: float,
    h2o2_M: float,
    volume_L: float = 1.0,
) -> CarbonBreakdown:
    """공정 조건에 대한 탄소 배출량 분해 계산."""
    heating = compute_heating_emission(temp_C, time_min, volume_L)
    acid = compute_acid_emission(h2so4_M, volume_L)
    h2o2 = compute_h2o2_emission(h2o2_M, volume_L)
    return CarbonBreakdown(
        heating_kg=heating,
        acid_kg=acid,
        h2o2_kg=h2o2,
        total_kg=heating + acid + h2o2,
    )


def generate_reduction_recommendations(
    breakdown: CarbonBreakdown,
    temp_C: float,
    time_min: float,
    h2so4_M: float,
    h2o2_M: float,
) -> list[str]:
    """탄소 배출 감축 추천 생성."""
    recs: list[str] = []

    # 가열이 최대 기여원인 경우
    if breakdown.heating_pct > 50:
        if temp_C > 60:
            recs.append(
                f"🌡️ 가열이 전체 배출의 {breakdown.heating_pct:.0f}%를 차지합니다. "
                f"온도를 {temp_C}°C → {max(temp_C - 15, 40)}°C로 낮추면 "
                f"가열 배출을 약 {(15 / max(temp_C - 25, 1)) * 100:.0f}% 줄일 수 있습니다."
            )
        if time_min > 120:
            recs.append(
                f"⏱️ 반응 시간 {time_min}분은 열 유지 에너지를 증가시킵니다. "
                f"포화 구간 이후 시간을 단축하면 불필요한 에너지 소비를 줄일 수 있습니다."
            )

    # H₂O₂가 높은 기여인 경우
    if breakdown.h2o2_pct > 30 and h2o2_M > 0.5:
        recs.append(
            f"🧪 H₂O₂ 생산이 전체 배출의 {breakdown.h2o2_pct:.0f}%입니다. "
            f"H₂O₂ 농도를 {h2o2_M:.2f}M → {max(h2o2_M * 0.6, 0.15):.2f}M로 줄이면 "
            f"약 {breakdown.h2o2_kg * 0.4:.4f} kg CO₂를 절감할 수 있습니다."
        )

    # H₂SO₄ 관련
    if h2so4_M > 1.5:
        recs.append(
            f"⚗️ H₂SO₄ 농도 {h2so4_M:.2f}M은 높은 편입니다. "
            f"1.0M 수준으로 낮춰도 회수율 차이가 크지 않을 수 있으며, "
            f"산 생산 배출을 약 {(h2so4_M - 1.0) / h2so4_M * 100:.0f}% 줄일 수 있습니다."
        )

    # 일반 추천
    if not recs:
        recs.append(
            "✅ 현재 조건은 비교적 낮은 탄소 배출 수준입니다. "
            "추가 감축을 위해 재생에너지 전력 사용을 고려해보세요."
        )

    # 재생에너지 전환 효과 항상 표시
    recs.append(
        f"♻️ 재생에너지 전력(0.05 kg CO₂/kWh) 전환 시 가열 배출을 "
        f"약 {(1 - 0.05 / 0.459) * 100:.0f}% 감축할 수 있습니다."
    )

    return recs
