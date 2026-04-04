"""Kinetics 시각화 화면."""

import streamlit as st
import pandas as pd

from src.sustainability.carbon_proxy import compute_carbon_proxy
from src.visualization.kinetics_plot import create_kinetics_line_plot


def render_kinetics_result(
    kinetics_data: pd.DataFrame,
    saturation_note: str | None,
    condition: dict[str, float],
    carbon_normalized_start: float,
    carbon_normalized_end: float,
) -> None:
    """Kinetics 결과 화면 렌더링."""
    st.header("⏱️ Kinetics 분석")

    # Line plot
    fig = create_kinetics_line_plot(kinetics_data)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # 탄소 부담 변화 안내
    st.subheader("🌱 반응 시간에 따른 탄소 부담 변화")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("시작 (1분)", f"{carbon_normalized_start:.3f}")
    with col2:
        st.metric("종료 (360분)", f"{carbon_normalized_end:.3f}")
    with col3:
        delta = carbon_normalized_end - carbon_normalized_start
        st.metric("증가량", f"+{delta:.3f}")

    st.caption(
        "반응 시간이 길어질수록 탄소 부담이 증가합니다. "
        "포화 구간 이후의 추가 시간은 자원 효율을 낮출 수 있습니다."
    )

    st.divider()

    # 포화 구간 해석
    if saturation_note:
        st.subheader("📈 포화 구간 분석")
        st.info(saturation_note)
    else:
        st.info("분석 범위 내에서 뚜렷한 포화 구간이 감지되지 않았습니다.")
