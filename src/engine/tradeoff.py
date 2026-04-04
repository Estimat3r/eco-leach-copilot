"""Trade-off 해석 텍스트 생성."""

from src.models import PredictionResult


def generate_tradeoff_summary(
    result_a: PredictionResult,
    result_b: PredictionResult,
    carbon_a: float,
    carbon_b: float,
) -> str:
    """두 조건 간 trade-off 해석 텍스트 생성.

    포함 가능한 해석:
    - 회수율 증가 대비 탄소 증가
    - 저온 조건의 효율성
    - 추가 시간 투입의 한계
    """
    lines: list[str] = []

    # 평균 회수율 계산
    avg_a = sum(result_a.leach_rates.values()) / len(result_a.leach_rates)
    avg_b = sum(result_b.leach_rates.values()) / len(result_b.leach_rates)

    recovery_diff = avg_b - avg_a
    carbon_diff = carbon_b - carbon_a

    # 회수율/탄소 비교 해석
    if recovery_diff < 0 and carbon_diff < 0:
        lines.append(
            f"조건 B는 조건 A 대비 회수율이 {abs(recovery_diff):.1f}% 낮지만, "
            f"탄소 부담은 {abs(carbon_diff):.1f}% 적습니다."
        )
    elif recovery_diff > 0 and carbon_diff > 0:
        lines.append(
            f"조건 B는 조건 A 대비 회수율이 {abs(recovery_diff):.1f}% 높지만, "
            f"탄소 부담도 {abs(carbon_diff):.1f}% 증가합니다."
        )
    elif recovery_diff > 0 and carbon_diff <= 0:
        lines.append(
            f"조건 B는 조건 A 대비 회수율이 {abs(recovery_diff):.1f}% 높으면서, "
            f"탄소 부담은 {abs(carbon_diff):.1f}% 적어 더 효율적입니다."
        )
    else:
        lines.append(
            f"조건 B는 조건 A 대비 회수율이 {abs(recovery_diff):.1f}% 낮고, "
            f"탄소 부담도 {abs(carbon_diff):.1f}% 높아 비효율적입니다."
        )

    # 탄소 부담 관련 추가 해석
    if carbon_b < carbon_a:
        lines.append("온도를 낮추면 탄소 부담을 줄일 수 있지만, 회수율도 감소합니다.")
    elif carbon_b > carbon_a and recovery_diff < 1.0:
        lines.append("추가 자원 투입 대비 회수율 향상이 미미하여, 자원 효율이 낮습니다.")

    return "\n".join(lines)
