"""Eco-Leach Copilot — Streamlit 앱 엔트리포인트."""

import streamlit as st

st.set_page_config(
    page_title="에코리치 | 폐배터리 침출 시뮬레이터",
    page_icon="🔋",
    layout="wide",
)

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


def main():
    # 데이터 로딩
    try:
        dataset = load_data()
    except (FileNotFoundError, ValueError) as e:
        st.error(f"❌ 데이터 로딩 실패: {e}")
        st.stop()

    supported_ranges = compute_supported_ranges(dataset)

    # 탭 구성
    tab_sim, tab_chat = st.tabs(["🔬 시뮬레이터", "🤖 AI 어시스턴트"])

    with tab_sim:
        condition_a, mode, condition_b = render_sidebar()

        # 단일 시뮬레이션
        if mode == "single":
            validation = validate_input(condition_a, supported_ranges)
            if not validation.is_valid:
                for err in validation.errors:
                    st.error(f"❌ {err}")
                st.stop()
            try:
                result = predict(condition_a, dataset)
                carbon = _compute_carbon(condition_a)
                recs = generate_reduction_recommendations(
                    carbon, condition_a["temp_C"], condition_a["time_min"],
                    condition_a["h2so4_M"], condition_a["h2o2_M"],
                )
                render_single_result(result, carbon, recs)
                # 챗봇용 세션 저장
                st.session_state["last_condition"] = condition_a
                st.session_state["last_result"] = {
                    "leach_rates": result.leach_rates,
                    "carbon_total_kg": carbon.total_kg,
                }
            except Exception as e:
                st.error(f"❌ 시뮬레이션 오류: {e}")

        # 조건 비교
        elif mode == "compare":
            if condition_b is None:
                st.warning("조건 B를 입력해주세요.")
                st.stop()
            val_a = validate_input(condition_a, supported_ranges)
            val_b = validate_input(condition_b, supported_ranges)
            if not val_a.is_valid:
                for err in val_a.errors:
                    st.error(f"❌ 조건 A: {err}")
                st.stop()
            if not val_b.is_valid:
                for err in val_b.errors:
                    st.error(f"❌ 조건 B: {err}")
                st.stop()
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

        # Kinetics
        elif mode == "kinetics":
            validation = validate_input(condition_a, supported_ranges)
            if not validation.is_valid:
                for err in validation.errors:
                    st.error(f"❌ {err}")
                st.stop()
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
                render_kinetics_result(
                    kinetics_df, saturation_note, condition_a,
                    carbon_start, carbon_end,
                )
                st.session_state["last_condition"] = condition_a
            except Exception as e:
                st.error(f"❌ Kinetics 분석 오류: {e}")

    with tab_chat:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            st.error("❌ Gemini API 키가 설정되지 않았습니다. .streamlit/secrets.toml을 확인하세요.")
            st.stop()

        render_chatbot(
            api_key=api_key,
            condition=st.session_state.get("last_condition"),
            last_result=st.session_state.get("last_result"),
        )


if __name__ == "__main__":
    main()
