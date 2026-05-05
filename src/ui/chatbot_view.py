"""AI 챗봇 화면 구현 — 차트 생성 기능 포함."""

from __future__ import annotations
import streamlit as st
import pandas as pd

# CSS 스타일 추가
st.markdown("""
<style>
/* 예시 질문 버튼 스타일 - 둥근 캡슐형 */
div[data-testid="stVerticalBlock"] button[key^="example_"] {
    background: white !important;
    border: 2px solid #e0e0e0 !important;
    border-radius: 50px !important;
    padding: 1.2rem 1.5rem !important;
    height: auto !important;
    min-height: 4rem !important;
    text-align: left !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    color: #333 !important;
    line-height: 1.5 !important;
    white-space: normal !important;
    word-wrap: break-word !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stVerticalBlock"] button[key^="example_"]:hover {
    background: #f5f5f5 !important;
    border-color: #bdbdbd !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}
</style>
""", unsafe_allow_html=True)

from src.chatbot.engine import build_context_message, chat, get_client
from src.engine.predictor import predict
from src.engine.kinetics import compute_kinetics, detect_saturation
from src.sustainability.carbon_emission import compute_carbon_emission
from src.visualization.comparison_plot import create_comparison_bar_chart
from src.visualization.carbon_plot import create_carbon_comparison_grouped
from src.visualization.kinetics_plot import create_kinetics_line_plot

EXAMPLE_QUESTIONS = [
    "Ni 회수율 90% 이상이면서 탄소 배출 최소화하는 조건은?",
    "온도 60°C와 80°C 조건의 회수율·탄소 비교 그래프 그려줘",
    "H₂SO₄ 1.0M과 2.0M 조건을 비교해줘",
    "75°C, H₂SO₄ 1.0M, H₂O₂ 0.5M 조건의 시간별 침출률 그래프 그려줘",
    "현재 조건에서 탄소 배출을 줄이는 방법은?",
]


def _run_comparison_chart(dataset: pd.DataFrame, chart_req: dict) -> None:
    """비교 차트 생성 및 렌더링."""
    ca = chart_req["condition_a"]
    cb = chart_req["condition_b"]
    label_a = chart_req.get("label_a", "조건 A")
    label_b = chart_req.get("label_b", "조건 B")

    # 기본값 보완
    for c in [ca, cb]:
        c.setdefault("pulp_density_gL", 100.0)

    result_a = predict(ca, dataset)
    result_b = predict(cb, dataset)
    carbon_a = compute_carbon_emission(ca["temp_C"], ca["time_min"], ca["h2so4_M"], ca["h2o2_M"])
    carbon_b = compute_carbon_emission(cb["temp_C"], cb["time_min"], cb["h2so4_M"], cb["h2o2_M"])

    # 조건 요약
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{label_a}**")
        st.caption(f"{ca['temp_C']}°C / {ca['time_min']}분 / H₂SO₄ {ca['h2so4_M']}M / H₂O₂ {ca['h2o2_M']}M")
    with col2:
        st.markdown(f"**{label_b}**")
        st.caption(f"{cb['temp_C']}°C / {cb['time_min']}분 / H₂SO₄ {cb['h2so4_M']}M / H₂O₂ {cb['h2o2_M']}M")

    fig_metals = create_comparison_bar_chart(
        result_a.leach_rates, result_b.leach_rates,
        labels=(label_a, label_b),
    )
    st.plotly_chart(fig_metals, use_container_width=True)

    fig_carbon = create_carbon_comparison_grouped(carbon_a, carbon_b)
    st.plotly_chart(fig_carbon, use_container_width=True)


def _run_kinetics_chart(dataset: pd.DataFrame, chart_req: dict) -> None:
    """Kinetics 차트 생성 및 렌더링."""
    condition = {
        "temp_C": chart_req["temp_C"],
        "h2so4_M": chart_req["h2so4_M"],
        "h2o2_M": chart_req["h2o2_M"],
        "pulp_density_gL": chart_req.get("pulp_density_gL", 100.0),
    }
    st.caption(
        f"조건: {condition['temp_C']}°C / H₂SO₄ {condition['h2so4_M']}M / "
        f"H₂O₂ {condition['h2o2_M']}M / 고액비 {condition['pulp_density_gL']}g/L"
    )
    kinetics_df = compute_kinetics(
        temp_C=condition["temp_C"],
        h2so4_M=condition["h2so4_M"],
        h2o2_M=condition["h2o2_M"],
        pulp_density_gL=condition["pulp_density_gL"],
        dataset=dataset,
    )
    fig = create_kinetics_line_plot(kinetics_df)
    st.plotly_chart(fig, use_container_width=True)

    note = detect_saturation(kinetics_df)
    if note:
        st.info(note)


def render_chatbot(
    api_key: str,
    dataset: pd.DataFrame,
    condition: dict[str, float] | None = None,
    last_result: dict | None = None,
) -> None:
    """AI 챗봇 화면 렌더링."""
    st.markdown("""
<div style="text-align: center; padding: 1rem 0 0.5rem 0;">
    <h2 style="margin: 0; color: #1565c0;">🤖 AI 공정 어시스턴트</h2>
    <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 1rem;">침출 공정 최적화, 탄소 감축, 그래프 생성 등 무엇이든 물어보세요</p>
</div>
""", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "gemini_client" not in st.session_state:
        try:
            st.session_state.gemini_client = get_client(api_key)
        except Exception as e:
            st.error(f"❌ AI 초기화 실패: {e}")
            return

    # 현재 조건 컨텍스트
    if condition:
        with st.expander("📋 현재 시뮬레이터 조건 (챗봇이 참고 중)", expanded=False):
            st.code(build_context_message(condition, last_result), language=None)

    # 예시 질문
    st.markdown("**💡 예시 질문**")
    
    for i, q in enumerate(EXAMPLE_QUESTIONS):
        if st.button(q, key=f"example_{i}", use_container_width=True):
            st.session_state.pending_question = q

    st.divider()

    # 대화 히스토리 표시
    for msg in st.session_state.chat_history:
        avatar = "🧑‍🔬" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            # 저장된 차트 재렌더링
            if msg.get("chart_req"):
                _render_chart(dataset, msg["chart_req"])

    pending = st.session_state.pop("pending_question", None)
    user_input = st.chat_input("공정 조건, 탄소 감축, 그래프 요청 등 질문하세요...")
    query = pending or user_input

    if query:
        context = build_context_message(condition, last_result)
        full_message = f"{context}\n\n사용자 질문: {query}" if context else query

        with st.chat_message("user", avatar="🧑‍🔬"):
            st.markdown(query)
        st.session_state.chat_history.append({"role": "user", "content": query})

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("분석 중..."):
                try:
                    answer, chart_req = chat(
                        st.session_state.gemini_client,
                        st.session_state.chat_history[:-1],
                        full_message,
                    )
                except Exception as e:
                    answer, chart_req = f"❌ 응답 오류: {e}", None

            st.markdown(answer)
            if chart_req:
                _render_chart(dataset, chart_req)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
            "chart_req": chart_req,
        })

    if st.session_state.chat_history:
        if st.button("🗑️ 대화 초기화", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()


def _render_chart(dataset: pd.DataFrame, chart_req: dict) -> None:
    """차트 타입에 따라 렌더링."""
    try:
        if chart_req["type"] == "comparison":
            _run_comparison_chart(dataset, chart_req)
        elif chart_req["type"] == "kinetics":
            _run_kinetics_chart(dataset, chart_req)
    except Exception as e:
        st.warning(f"차트 생성 중 오류: {e}")
