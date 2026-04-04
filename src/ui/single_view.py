"""단일 조건 결과 화면 구현."""

import streamlit as st

from src.models import PredictionResult
from src.sustainability.carbon_emission import CarbonBreakdown
from src.visualization.carbon_plot import create_carbon_breakdown_pie


METAL_LABELS = {
    "Li_pct": ("🔋 Li", "리튬"),
    "Ni_pct": ("🟢 Ni", "니켈"),
    "Co_pct": ("🟠 Co", "코발트"),
    "Mn_pct": ("🟣 Mn", "망간"),
}


def render_single_result(
    prediction: PredictionResult,
    carbon: CarbonBreakdown,
    recommendations: list[str],
) -> None:
    """단일 조건 결과 화면 렌더링."""
    st.header("📊 시뮬레이션 결과")
    st.divider()

    # 금속별 침출률
    st.subheader("금속별 침출률")
    cols = st.columns(4)
    for i, (key, (icon, name)) in enumerate(METAL_LABELS.items()):
        value = prediction.leach_rates.get(key, 0.0)
        with cols[i]:
            st.metric(label=f"{icon} {name}", value=f"{value:.1f}%")

    st.divider()

    # 탄소 배출량 (kg CO₂)
    st.subheader("🏭 탄소 배출량 분석")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.metric("총 CO₂ 배출량", f"{carbon.total_kg:.4f} kg CO₂")
        st.caption("1L 반응 용액 기준 (batch)")

        # 분해 테이블
        st.markdown("**배출원별 분해**")
        st.dataframe({
            "배출원": ["🔥 가열 에너지", "⚗️ H₂SO₄ 생산", "🧪 H₂O₂ 생산"],
            "배출량 (kg CO₂)": [
                f"{carbon.heating_kg:.4f}",
                f"{carbon.acid_kg:.4f}",
                f"{carbon.h2o2_kg:.4f}",
            ],
            "비율": [
                f"{carbon.heating_pct:.1f}%",
                f"{carbon.acid_pct:.1f}%",
                f"{carbon.h2o2_pct:.1f}%",
            ],
        }, use_container_width=True, hide_index=True)

    with col2:
        fig = create_carbon_breakdown_pie(carbon)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # 탄소 감축 추천
    st.subheader("💡 탄소 감축 추천")
    for rec in recommendations:
        st.info(rec)

    st.divider()

    # 해석 텍스트
    _render_interpretation(prediction, carbon)


def _render_interpretation(
    prediction: PredictionResult,
    carbon: CarbonBreakdown,
) -> None:
    """해석 텍스트 생성."""
    avg_recovery = sum(prediction.leach_rates.values()) / len(prediction.leach_rates)

    if avg_recovery >= 80 and carbon.total_kg < 0.02:
        text = "✅ 높은 회수율과 낮은 탄소 배출을 동시에 달성하는 우수한 조건입니다."
    elif avg_recovery >= 80 and carbon.total_kg >= 0.02:
        text = "⚠️ 회수율은 높지만 탄소 배출도 큽니다. 위 감축 추천을 참고하세요."
    elif avg_recovery < 50:
        text = "📉 회수율이 낮습니다. 조건 조정 시 탄소 배출 증가에 유의하세요."
    else:
        text = "📊 중간 수준의 회수율입니다. 탄소 배출과의 균형을 고려하여 조건을 조정해보세요."

    st.info(text)
