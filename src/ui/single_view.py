"""단일 조건 결과 화면 구현."""

import streamlit as st

from src.models import PredictionResult
from src.ui.warnings import render_confidence_badge, render_warnings


METAL_LABELS = {
    "Li_pct": ("🔋 Li", "리튬"),
    "Ni_pct": ("🟢 Ni", "니켈"),
    "Co_pct": ("🟠 Co", "코발트"),
    "Mn_pct": ("🟣 Mn", "망간"),
}


def render_single_result(
    prediction: PredictionResult,
    carbon_normalized: float,
    carbon_raw: float,
) -> None:
    """단일 조건 결과 화면 렌더링."""
    st.header("📊 시뮬레이션 결과")

    # 경고 메시지
    if prediction.warnings:
        render_warnings(prediction.warnings)

    # 신뢰도 배지
    render_confidence_badge(prediction.confidence_tier)

    st.divider()

    # 4개 금속 침출률 metric 카드
    st.subheader("금속별 침출률")
    cols = st.columns(4)
    for i, (key, (icon, name)) in enumerate(METAL_LABELS.items()):
        value = prediction.leach_rates.get(key, 0.0)
        with cols[i]:
            st.metric(label=f"{icon} {name}", value=f"{value:.1f}%")

    st.divider()

    # Carbon Proxy Index
    st.subheader("🌱 Carbon Proxy Index")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(min(carbon_normalized, 1.0))
    with col2:
        st.metric("탄소 부담", f"{carbon_normalized:.2f}")

    st.caption(f"Raw 값: {carbon_raw:.4f} (0에 가까울수록 탄소 부담이 적음)")

    st.divider()

    # 해석 텍스트
    _render_interpretation(prediction, carbon_normalized)


def _render_interpretation(
    prediction: PredictionResult,
    carbon_normalized: float,
) -> None:
    """1~2줄 해석 텍스트 생성."""
    avg_recovery = sum(prediction.leach_rates.values()) / len(prediction.leach_rates)

    if avg_recovery >= 80 and carbon_normalized <= 0.4:
        text = "✅ 높은 회수율과 낮은 탄소 부담을 동시에 달성하는 우수한 조건입니다."
    elif avg_recovery >= 80 and carbon_normalized > 0.4:
        text = "⚠️ 회수율은 높지만 탄소 부담도 큽니다. 자원 효율 개선을 위해 온도나 시약 농도를 낮춰보세요."
    elif avg_recovery < 50:
        text = "📉 회수율이 낮습니다. 온도 또는 반응 시간을 높이면 개선될 수 있지만, 탄소 부담 증가에 유의하세요."
    else:
        text = "📊 중간 수준의 회수율입니다. 탄소 부담과의 균형을 고려하여 조건을 조정해보세요."

    st.info(text)
