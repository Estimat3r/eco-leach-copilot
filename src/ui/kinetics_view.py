"""Kinetics 시각화 화면."""

import streamlit as st
import pandas as pd

from src.models import PredictionResult
from src.sustainability.carbon_emission import CarbonBreakdown
from src.visualization.kinetics_plot import create_kinetics_line_plot
from src.ui.warnings import render_confidence_badge, render_warnings


def render_kinetics_result(
    kinetics_data: pd.DataFrame,
    saturation_note: str | None,
    condition: dict[str, float],
    carbon_start: CarbonBreakdown,
    carbon_end: CarbonBreakdown,
    base_result: PredictionResult,
) -> None:
    """Kinetics 결과 화면 렌더링."""
    st.header("⏱️ Kinetics 분석")

    # 신뢰도 표시
    render_confidence_badge(base_result.confidence_tier)
    if base_result.warnings:
        render_warnings(base_result.warnings)
    
    st.markdown("---")

    fig = create_kinetics_line_plot(kinetics_data)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # 반응 시간에 따른 탄소 배출 변화
    st.subheader("🏭 반응 시간에 따른 탄소 배출 변화")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("1분 시점", f"{carbon_start.total_kg:.4f} kg CO₂")
    with col2:
        st.metric("360분 시점", f"{carbon_end.total_kg:.4f} kg CO₂")
    with col3:
        delta = carbon_end.total_kg - carbon_start.total_kg
        st.metric("증가량", f"+{delta:.4f} kg CO₂")

    st.caption(
        "반응 시간이 길어질수록 열 유지 에너지로 인해 탄소 배출이 증가합니다. "
        "포화 구간 이후의 추가 시간은 회수율 개선 없이 배출만 늘릴 수 있습니다."
    )

    st.divider()

    # 포화 구간 분석
    if saturation_note:
        st.subheader("📈 포화 구간 분석")
        st.info(saturation_note)
    else:
        st.info("분석 범위 내에서 뚜렷한 포화 구간이 감지되지 않았습니다.")
