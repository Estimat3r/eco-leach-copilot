"""에코리치 — NCM811 폐배터리 침출 공정 시뮬레이터."""

import streamlit as st

st.set_page_config(
    page_title="에코리치 | 폐배터리 침출 시뮬레이터",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 전역 CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* 전체 폰트 적용 */
html, body, [class*="css"], .stMarkdown, .stButton button, h1, h2, h3, p, div {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* 전체 여백 조정 */
.block-container { padding-top: 3rem; padding-bottom: 1rem; }

/* 섹션 간격 약간 축소 */
div[data-testid="stVerticalBlock"] > div { margin-bottom: -0.3rem; }

/* 탭 크기 키우기 */
button[data-baseweb="tab"] {
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.4rem !important;
}

/* 네비게이션 버튼 스타일 - 둥근 캡슐형 */
div[data-testid="column"] button[key*="back_"],
div[data-testid="column"] button[key*="go_"],
div[data-testid="column"] button[key*="nav_"] {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    height: 3.2rem !important;
    border-radius: 50px !important;
    padding: 0.8rem 2rem !important;
    border: 2px solid #e0e0e0 !important;
    background: white !important;
    color: #333 !important;
    transition: all 0.3s ease !important;
}

div[data-testid="column"] button[key*="back_"]:hover,
div[data-testid="column"] button[key*="go_"]:hover,
div[data-testid="column"] button[key*="nav_"]:hover {
    background: #f5f5f5 !important;
    border-color: #bdbdbd !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}

/* 랜딩 버튼 스타일 - 둥근 캡슐형 */
div[data-testid="column"] button[kind="primary"],
div[data-testid="column"] button[kind="secondary"] {
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    height: 4.5rem !important;
    border-radius: 50px !important;
    padding: 1rem 2rem !important;
    border: none !important;
    transition: all 0.3s ease !important;
}

div[data-testid="column"] button[kind="primary"]:hover,
div[data-testid="column"] button[kind="secondary"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
}

/* metric 카드 간격 */
div[data-testid="metric-container"] { padding: 0.4rem 0 !important; }

/* 사이드바 타이틀 */
section[data-testid="stSidebar"] .stMarkdown h1 { font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

from src.data.loader import load_dataset
from src.data.validator import compute_supported_ranges, validate_input
from src.engine.predictor import predict
from src.engine.tradeoff import generate_tradeoff_summary
from src.engine.kinetics import compute_kinetics, detect_saturation
from src.sustainability.carbon_emission import (
    compute_carbon_emission,
    generate_reduction_recommendations,
)
from src.ui.sidebar import render_sidebar
from src.ui.single_view import render_single_result
from src.ui.compare_view import render_compare_result
from src.ui.kinetics_view import render_kinetics_result
from src.ui.chatbot_view import render_chatbot


@st.cache_data
def load_data():
    return load_dataset()


def _compute_carbon(condition: dict[str, float]):
    return compute_carbon_emission(
        condition["temp_C"],
        condition["time_min"],
        condition["h2so4_M"],
        condition["h2o2_M"],
    )


def render_landing():
    """랜딩 페이지 — 로고 + 기능 선택."""
    st.markdown("<br><br><br>", unsafe_allow_html=True)

    # 로고 영역
    col_l, col_c, col_r = st.columns([1, 3, 1])
    with col_c:
        st.markdown("""
<div style="text-align:center; padding: 3rem 0 2rem 0;">
  <div style="font-size: 6rem; margin-bottom: 0.5rem;">🔋</div>
  <div style="font-size: 3.5rem; font-weight: 800; color: #1a7a4a; letter-spacing: -1px; margin-bottom: 0.8rem;">에코리치</div>
  <div style="font-size: 1.3rem; color: #333; margin-top: 0.6rem; font-weight: 500; line-height: 1.6;">
    지속 가능한 폐배터리 재활용을 위한 침출 공정 최적화 플랫폼
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # 기능 선택 버튼
    col_l, col1, col_gap, col2, col_r = st.columns([0.5, 2.5, 0.4, 2.5, 0.5])

    with col1:
        st.markdown("""
<div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
     border-radius: 50px; padding: 2.5rem 1.5rem; text-align: center;
     border: none; margin-bottom: 0.8rem; box-shadow: 0 4px 16px rgba(0,0,0,0.08);">
  <div style="font-size: 3rem; margin-bottom: 0.5rem;">🔬</div>
  <div style="font-size: 1.5rem; font-weight: 700; color: #1a7a4a; margin: 0.5rem 0 0.5rem;">공정 시뮬레이터</div>
  <div style="font-size: 1rem; color: #555; line-height: 1.6;">
    공정 조건 입력 → 금속 회수율 예측<br>탄소 배출량 분석 · 조건 비교 · Kinetics
  </div>
</div>
""", unsafe_allow_html=True)
        if st.button("🔬 시뮬레이터 시작", key="btn_sim", use_container_width=True, type="primary"):
            st.session_state["page"] = "simulator"
            st.rerun()

    with col2:
        st.markdown("""
<div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb);
     border-radius: 50px; padding: 2.5rem 1.5rem; text-align: center;
     border: none; margin-bottom: 0.8rem; box-shadow: 0 4px 16px rgba(0,0,0,0.08);">
  <div style="font-size: 3rem; margin-bottom: 0.5rem;">🤖</div>
  <div style="font-size: 1.5rem; font-weight: 700; color: #1565c0; margin: 0.5rem 0 0.5rem;">AI 어시스턴트</div>
  <div style="font-size: 1rem; color: #555; line-height: 1.6;">
    자연어로 질문 → 최적 조건 추천<br>그래프 생성 · 탄소 감축 전략 제안
  </div>
</div>
""", unsafe_allow_html=True)
        if st.button("🤖 AI 어시스턴트 시작", key="btn_chat", use_container_width=True):
            st.session_state["page"] = "chatbot"
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    # 하단 특징 요약
    col_l, col_c, col_r = st.columns([1, 4, 1])
    with col_c:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
<div style="text-align:center; padding: 1rem; background:white; border-radius:30px; border: 2px solid #f0f0f0;">
  <div style="font-size:1.5rem;">📊</div>
  <div style="font-size:0.85rem; font-weight:600; margin-top:0.3rem;">LCA 기반 탄소 계산</div>
  <div style="font-size:0.75rem; color:#777;">실제 emission factor 적용</div>
</div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
<div style="text-align:center; padding: 1rem; background:white; border-radius:30px; border: 2px solid #f0f0f0;">
  <div style="font-size:1.5rem;">⚖️</div>
  <div style="font-size:0.85rem; font-weight:600; margin-top:0.3rem;">회수율 vs 탄소 Trade-off</div>
  <div style="font-size:0.75rem; color:#777;">균형 조건 탐색 지원</div>
</div>""", unsafe_allow_html=True)
        with c3:
            st.markdown("""
<div style="text-align:center; padding: 1rem; background:white; border-radius:30px; border: 2px solid #f0f0f0;">
  <div style="font-size:1.5rem;">🤖</div>
  <div style="font-size:0.85rem; font-weight:600; margin-top:0.3rem;">AI 챗봇 연동</div>
  <div style="font-size:0.75rem; color:#777;">자연어 질문 · 차트 생성</div>
</div>""", unsafe_allow_html=True)


def render_simulator_page(dataset, supported_ranges):
    """시뮬레이터 페이지."""
    # 상단 네비게이션
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_l, col1, col2, col3, col_r = st.columns([1, 1.5, 1.5, 1.5, 1])
    with col1:
        if st.button("🏠 홈", key="back_sim", use_container_width=True):
            st.session_state["page"] = "landing"
            st.rerun()
    with col2:
        st.markdown("""
<div style="text-align: center; padding: 0.6rem 0;">
    <span style="font-size: 1.3rem; font-weight: 700; color: #1a7a4a;">🔬 시뮬레이터</span>
</div>
""", unsafe_allow_html=True)
    with col3:
        if st.button("🤖 AI 어시스턴트", key="nav_chat_from_sim", use_container_width=True):
            st.session_state["page"] = "chatbot"
            st.rerun()
    
    st.divider()

    condition_a, mode, condition_b = render_sidebar()

    if mode == "single":
        validation = validate_input(condition_a, supported_ranges)
        if not validation.is_valid:
            for err in validation.errors:
                st.error(f"❌ {err}")
            return
        try:
            result = predict(condition_a, dataset)
            carbon = _compute_carbon(condition_a)
            recs = generate_reduction_recommendations(
                carbon, condition_a["temp_C"], condition_a["time_min"],
                condition_a["h2so4_M"], condition_a["h2o2_M"],
            )
            render_single_result(result, carbon, recs)
            st.session_state["last_condition"] = condition_a
            st.session_state["last_result"] = {
                "leach_rates": result.leach_rates,
                "carbon_total_kg": carbon.total_kg,
            }
        except Exception as e:
            st.error(f"❌ 시뮬레이션 오류: {e}")

    elif mode == "compare":
        if condition_b is None:
            st.warning("조건 B를 입력해주세요.")
            return
        val_a = validate_input(condition_a, supported_ranges)
        val_b = validate_input(condition_b, supported_ranges)
        if not val_a.is_valid:
            for err in val_a.errors:
                st.error(f"❌ 조건 A: {err}")
            return
        if not val_b.is_valid:
            for err in val_b.errors:
                st.error(f"❌ 조건 B: {err}")
            return
        try:
            result_a = predict(condition_a, dataset)
            result_b = predict(condition_b, dataset)
            carbon_a = _compute_carbon(condition_a)
            carbon_b = _compute_carbon(condition_b)
            tradeoff = generate_tradeoff_summary(result_a, result_b, carbon_a, carbon_b)
            render_compare_result(result_a, result_b, carbon_a, carbon_b, tradeoff)
            st.session_state["last_condition"] = condition_a
        except Exception as e:
            st.error(f"❌ 비교 시뮬레이션 오류: {e}")

    elif mode == "kinetics":
        validation = validate_input(condition_a, supported_ranges)
        if not validation.is_valid:
            for err in validation.errors:
                st.error(f"❌ {err}")
            return
        try:
            kinetics_df = compute_kinetics(
                temp_C=condition_a["temp_C"],
                h2so4_M=condition_a["h2so4_M"],
                h2o2_M=condition_a["h2o2_M"],
                pulp_density_gL=condition_a["pulp_density_gL"],
                dataset=dataset,
            )
            saturation_note = detect_saturation(kinetics_df)
            carbon_start = compute_carbon_emission(
                condition_a["temp_C"], 1.0,
                condition_a["h2so4_M"], condition_a["h2o2_M"],
            )
            carbon_end = compute_carbon_emission(
                condition_a["temp_C"], 360.0,
                condition_a["h2so4_M"], condition_a["h2o2_M"],
            )
            render_kinetics_result(kinetics_df, saturation_note, condition_a, carbon_start, carbon_end)
            st.session_state["last_condition"] = condition_a
        except Exception as e:
            st.error(f"❌ Kinetics 분석 오류: {e}")


def render_chatbot_page(dataset):
    """챗봇 페이지."""
    # 상단 네비게이션
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_l, col1, col2, col3, col_r = st.columns([1, 1.5, 1.5, 1.5, 1])
    with col1:
        if st.button("🏠 홈", key="back_chat", use_container_width=True):
            st.session_state["page"] = "landing"
            st.rerun()
    with col2:
        if st.button("🔬 시뮬레이터", key="nav_sim_from_chat", use_container_width=True):
            st.session_state["page"] = "simulator"
            st.rerun()
    with col3:
        st.markdown("""
<div style="text-align: center; padding: 0.6rem 0;">
    <span style="font-size: 1.3rem; font-weight: 700; color: #1565c0;">🤖 AI 어시스턴트</span>
</div>
""", unsafe_allow_html=True)
    
    st.divider()

    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        st.error("❌ OpenAI API 키가 설정되지 않았습니다.")
        return

    render_chatbot(
        api_key=api_key,
        dataset=dataset,
        condition=st.session_state.get("last_condition"),
        last_result=st.session_state.get("last_result"),
    )


def main():
    try:
        dataset = load_data()
    except (FileNotFoundError, ValueError) as e:
        st.error(f"❌ 데이터 로딩 실패: {e}")
        st.stop()

    supported_ranges = compute_supported_ranges(dataset)

    # 페이지 라우팅
    page = st.session_state.get("page", "landing")

    if page == "landing":
        render_landing()
    elif page == "simulator":
        render_simulator_page(dataset, supported_ranges)
    elif page == "chatbot":
        render_chatbot_page(dataset)


if __name__ == "__main__":
    main()
