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
/* 전체 여백 축소 */
.block-container { padding-top: 1.5rem; padding-bottom: 1rem; }

/* 섹션 간격 약간 축소 */
div[data-testid="stVerticalBlock"] > div { margin-bottom: -0.3rem; }

/* 탭 크기 키우기 */
button[data-baseweb="tab"] {
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.4rem !important;
}

/* 랜딩 버튼 스타일 */
.landing-btn button {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    height: 3.2rem !important;
    border-radius: 12px !important;
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
    st.markdown("<br><br>", unsafe_allow_html=True)

    # 로고 영역
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown("""
<div style="text-align:center; padding: 2rem 0 1.5rem 0;">
  <div style="font-size: 4rem; margin-bottom: 0.3rem;">🔋</div>
  <div style="font-size: 2.8rem; font-weight: 800; color: #1a7a4a; letter-spacing: -1px;">에코리치</div>
  <div style="font-size: 1.05rem; color: #555; margin-top: 0.4rem; font-weight: 400;">
    NCM811 폐배터리 침출 공정 최적화 시뮬레이터
  </div>
  <div style="font-size: 0.9rem; color: #888; margin-top: 0.3rem;">
    회수율과 탄소 배출, 둘 다 잡는다
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 기능 선택 버튼
    col_l, col1, col_gap, col2, col_r = st.columns([1, 2, 0.3, 2, 1])

    with col1:
        st.markdown("""
<div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
     border-radius: 16px; padding: 1.8rem 1.2rem; text-align: center;
     border: 1.5px solid #81c784; margin-bottom: 0.5rem;">
  <div style="font-size: 2.2rem;">🔬</div>
  <div style="font-size: 1.2rem; font-weight: 700; color: #1a7a4a; margin: 0.4rem 0 0.3rem;">공정 시뮬레이터</div>
  <div style="font-size: 0.85rem; color: #555; line-height: 1.5;">
    공정 조건 입력 → 금속 회수율 예측<br>탄소 배출량 분석 · 조건 비교 · Kinetics
  </div>
</div>
""", unsafe_allow_html=True)
        if st.button("시뮬레이터 시작 →", key="btn_sim", use_container_width=True, type="primary"):
            st.session_state["page"] = "simulator"
            st.rerun()

    with col2:
        st.markdown("""
<div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb);
     border-radius: 16px; padding: 1.8rem 1.2rem; text-align: center;
     border: 1.5px solid #64b5f6; margin-bottom: 0.5rem;">
  <div style="font-size: 2.2rem;">🤖</div>
  <div style="font-size: 1.2rem; font-weight: 700; color: #1565c0; margin: 0.4rem 0 0.3rem;">AI 어시스턴트</div>
  <div style="font-size: 0.85rem; color: #555; line-height: 1.5;">
    자연어로 질문 → 최적 조건 추천<br>그래프 생성 · 탄소 감축 전략 제안
  </div>
</div>
""", unsafe_allow_html=True)
        if st.button("AI 어시스턴트 시작 →", key="btn_chat", use_container_width=True):
            st.session_state["page"] = "chatbot"
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    # 하단 특징 요약
    col_l, col_c, col_r = st.columns([1, 4, 1])
    with col_c:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
<div style="text-align:center; padding: 0.8rem; background:#f9f9f9; border-radius:10px;">
  <div style="font-size:1.5rem;">📊</div>
  <div style="font-size:0.85rem; font-weight:600; margin-top:0.3rem;">LCA 기반 탄소 계산</div>
  <div style="font-size:0.75rem; color:#777;">실제 emission factor 적용</div>
</div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
<div style="text-align:center; padding: 0.8rem; background:#f9f9f9; border-radius:10px;">
  <div style="font-size:1.5rem;">⚖️</div>
  <div style="font-size:0.85rem; font-weight:600; margin-top:0.3rem;">회수율 vs 탄소 Trade-off</div>
  <div style="font-size:0.75rem; color:#777;">균형 조건 탐색 지원</div>
</div>""", unsafe_allow_html=True)
        with c3:
            st.markdown("""
<div style="text-align:center; padding: 0.8rem; background:#f9f9f9; border-radius:10px;">
  <div style="font-size:1.5rem;">🤖</div>
  <div style="font-size:0.85rem; font-weight:600; margin-top:0.3rem;">AI 챗봇 연동</div>
  <div style="font-size:0.75rem; color:#777;">자연어 질문 · 차트 생성</div>
</div>""", unsafe_allow_html=True)


def render_simulator_page(dataset, supported_ranges):
    """시뮬레이터 페이지."""
    # 상단 네비게이션
    col_back, col_title, col_chat = st.columns([1, 6, 1.5])
    with col_back:
        if st.button("← 홈", key="back_sim"):
            st.session_state["page"] = "landing"
            st.rerun()
    with col_title:
        st.markdown("<h2 style='margin:0; padding:0.2rem 0;'>🔬 공정 시뮬레이터</h2>", unsafe_allow_html=True)
    with col_chat:
        if st.button("🤖 AI 어시스턴트", key="go_chat"):
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
    col_back, col_title, col_sim = st.columns([1, 6, 1.5])
    with col_back:
        if st.button("← 홈", key="back_chat"):
            st.session_state["page"] = "landing"
            st.rerun()
    with col_title:
        st.markdown("<h2 style='margin:0; padding:0.2rem 0;'>🤖 AI 공정 어시스턴트</h2>", unsafe_allow_html=True)
    with col_sim:
        if st.button("🔬 시뮬레이터", key="go_sim"):
            st.session_state["page"] = "simulator"
            st.rerun()

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
