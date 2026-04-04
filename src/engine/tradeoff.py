"""Trade-off 해석 텍스트 생성 (kg CO₂ 기반)."""

from src.models import PredictionResult
from src.sustainability.carbon_emission import CarbonBreakdown


def generate_tradeoff_summary(
    result_a: PredictionResult,
    result_b: PredictionResult,
    carbon_a: CarbonBreakdown,
    carbon_b: CarbonBreakdown,
) -> str:
    """두 조건 간 trade-off 해석 텍스트 생성."""
    lines: list[str] = []

    avg_a = sum(result_a.leach_rates.values()) / len(result_a.leach_rates)
    avg_b = sum(result_b.leach_rates.values()) / len(result_b.leach_rates)

    recovery_diff = avg_b - avg_a
    carbon_diff_kg = carbon_b.total_kg - carbon_a.total_kg
    carbon_diff_pct = (carbon_diff_kg / carbon_a.total_kg * 100) if carbon_a.total_kg > 0 else 0

    # 회수율/탄소 비교
    if recovery_diff < 0 and carbon_diff_kg < 0:
        lines.append(
            f"조건 B는 평균 회수율이 {abs(recovery_diff):.1f}%p 낮지만, "
            f"탄소 배출은 {abs(carbon_diff_kg):.4f} kg CO₂ ({abs(carbon_diff_pct):.1f}%) 적습니다."
        )
    elif recovery_diff > 0 and carbon_diff_kg > 0:
        lines.append(
            f"조건 B는 평균 회수율이 {abs(recovery_diff):.1f}%p 높지만, "
            f"탄소 배출도 {abs(carbon_diff_kg):.4f} kg CO₂ ({abs(carbon_diff_pct):.1f}%) 증가합니다."
        )
        # 효율성 비율
        if recovery_diff > 0 and carbon_diff_kg > 0:
            efficiency = recovery_diff / (carbon_diff_kg * 1000)  # %p per g CO₂
            lines.append(f"회수율 1%p 향상당 추가 탄소 배출: {1/efficiency:.2f}g CO₂")
    elif recovery_diff > 0 and carbon_diff_kg <= 0:
        lines.append(
            f"조건 B는 회수율이 {abs(recovery_diff):.1f}%p 높으면서 "
            f"탄소 배출은 {abs(carbon_diff_kg):.4f} kg CO₂ 적어 더 효율적입니다."
        )
    else:
        lines.append(
            f"조건 B는 회수율이 {abs(recovery_diff):.1f}%p 낮고 "
            f"탄소 배출도 {abs(carbon_diff_kg):.4f} kg CO₂ 높아 비효율적입니다."
        )

    # 주요 배출원 차이 분석
    heat_diff = carbon_b.heating_kg - carbon_a.heating_kg
    if abs(heat_diff) > 0.001:
        direction = "증가" if heat_diff > 0 else "감소"
        lines.append(f"가열 에너지 배출 {direction}: {abs(heat_diff):.4f} kg CO₂")

    return "\n".join(lines)
