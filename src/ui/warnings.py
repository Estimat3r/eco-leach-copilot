"""경고/신뢰도 메시지 렌더링."""

import streamlit as st


CONFIDENCE_BADGES = {
    "high": ("🟢 높음", "success"),
    "medium": ("🟡 보통", "warning"),
    "low": ("🔴 낮음", "error"),
}


def render_confidence_badge(confidence_tier: str) -> None:
    """Confidence Tier 색상 배지를 렌더링."""
    label, badge_type = CONFIDENCE_BADGES.get(
        confidence_tier, ("⚪ 알 수 없음", "info")
    )
    if badge_type == "success":
        st.success(f"신뢰도: {label} — 데이터와 매우 유사한 조건입니다")
    elif badge_type == "warning":
        st.warning(f"신뢰도: {label} — 보간 기반 예측입니다")
    else:
        st.error(f"신뢰도: {label} — 데이터가 부족한 영역입니다. 결과를 참고용으로만 활용하세요")


def render_warnings(warnings: list[str]) -> None:
    """범위 밖 경고 메시지를 표시."""
    for w in warnings:
        st.warning(f"⚠️ {w}")
