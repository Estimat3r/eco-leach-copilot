"""조건 비교 결과 화면 구현."""

import streamlit as st

from src.models import PredictionResult
from src.ui.warnings import render_confidence_badge, render_warnings
from src.visualization.comparison_plot import (
    create_carbon_comparison_bar,
    create_comparison_bar_chart,
)


METAL_LABELS = {
    "Li_pct": "Li",
    "Ni_pct": "Ni",
    "Co_pct": "Co",
    "Mn_pct": "Mn",
}


def render_compare_result(
    result_a: PredictionResult,
    result_b: PredictionResult,
    carbon_a: float,
    carbon_b: float,
    tradeoff_summary: str,
) -> None:
    """비교 결과 화면 렌더링."""
    st.header("⚖️ 조건 비교 결과")

    # 경고 표시
    all_warnings = result_a.warnings + result_b.warnings
    if all_warnings:
        render_warnings(list(set(all_warnings)))

    # 신뢰도 배지 (양쪽)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("조건 A")
        render_confidence_badge(result_a.confidence_tier)
    with col2:
        st.subheader("조건 B")
        render_confidence_badge(result_b.confidence_tier)

    st.divider()

    # 비교 테이블
    st.subheader("📋 침출률 비교 테이블")
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

    st.divider()

    # 금속별 비교 차트
    st.subheader("📊 금속별 침출률 비교")
    fig_metals = create_comparison_bar_chart(
        result_a.leach_rates, result_b.leach_rates
    )
    st.plotly_chart(fig_metals, use_container_width=True)

    # Carbon Proxy 비교
    st.subheader("🌱 Carbon Proxy 비교")
    fig_carbon = create_carbon_comparison_bar(carbon_a, carbon_b)
    st.plotly_chart(fig_carbon, use_container_width=True)

    st.divider()

    # Trade-off Summary
    st.subheader("💡 Trade-off 해석")
    st.info(tradeoff_summary)
