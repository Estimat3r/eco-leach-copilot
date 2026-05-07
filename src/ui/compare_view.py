"""조건 비교 결과 화면 구현."""

import streamlit as st

from src.models import PredictionResult
from src.sustainability.carbon_emission import CarbonBreakdown
from src.visualization.comparison_plot import create_comparison_bar_chart
from src.visualization.carbon_plot import create_carbon_comparison_grouped
from src.ui.warnings import render_confidence_badge, render_warnings


METAL_LABELS = {
    "Li_pct": "Li",
    "Ni_pct": "Ni",
    "Co_pct": "Co",
    "Mn_pct": "Mn",
}


def render_compare_result(
    result_a: PredictionResult,
    result_b: PredictionResult,
    carbon_a: CarbonBreakdown,
    carbon_b: CarbonBreakdown,
    tradeoff_summary: str,
) -> None:
    """비교 결과 화면 렌더링."""
    st.header("⚖️ 조건 비교 결과")
    
    # 신뢰도 표시
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**조건 A 신뢰도**")
        render_confidence_badge(result_a.confidence_tier)
        if result_a.warnings:
            render_warnings(result_a.warnings)
    with col2:
        st.markdown("**조건 B 신뢰도**")
        render_confidence_badge(result_b.confidence_tier)
        if result_b.warnings:
            render_warnings(result_b.warnings)
    
    st.divider()

    # 침출률 비교 테이블
    st.subheader("📋 침출률 비교")
    table_data = {"금속": [], "조건 A (%)": [], "조건 B (%)": [], "차이 (%)": []}
    for key, name in METAL_LABELS.items():
        va = result_a.leach_rates.get(key, 0.0)
        vb = result_b.leach_rates.get(key, 0.0)
        table_data["금속"].append(name)
        table_data["조건 A (%)"].append(f"{va:.1f}")
        table_data["조건 B (%)"].append(f"{vb:.1f}")
        diff = vb - va
        sign = "+" if diff >= 0 else ""
        table_data["차이 (%)"].append(f"{sign}{diff:.1f}")

    st.dataframe(table_data, use_container_width=True, hide_index=True)

    # 금속별 비교 차트
    fig_metals = create_comparison_bar_chart(
        result_a.leach_rates, result_b.leach_rates
    )
    st.plotly_chart(fig_metals, use_container_width=True)

    st.divider()

    # 탄소 배출량 비교
    st.subheader("🏭 탄소 배출량 비교 (kg CO₂)")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("조건 A", f"{carbon_a.total_kg:.4f} kg")
    with col2:
        st.metric("조건 B", f"{carbon_b.total_kg:.4f} kg")
    with col3:
        diff = carbon_b.total_kg - carbon_a.total_kg
        pct = (diff / carbon_a.total_kg * 100) if carbon_a.total_kg > 0 else 0
        sign = "+" if diff >= 0 else ""
        st.metric("차이", f"{sign}{diff:.4f} kg", delta=f"{sign}{pct:.1f}%",
                  delta_color="inverse")

    fig_carbon = create_carbon_comparison_grouped(carbon_a, carbon_b)
    st.plotly_chart(fig_carbon, use_container_width=True)

    st.divider()

    # Trade-off 해석
    st.subheader("💡 Trade-off 해석")
    st.info(tradeoff_summary)
