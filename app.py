"""Eco-Leach Copilot — Streamlit 앱 엔트리포인트."""

import streamlit as st

st.set_page_config(
    page_title="Eco-Leach Copilot",
    page_icon="🔬",
    layout="wide",
)

import pandas as pd

from src.data.loader import load_dataset
from src.data.validator import compute_supported_ranges, validate_input
from src.engine.predictor import predict
from src.engine.tradeoff import generate_tradeoff_summary
from src.engine.kinetics import compute_kinetics, detect_saturation
from src.sustainability.carbon_proxy import (
    compute_carbon_proxy,
    compute_dataset_max_carbon,
    normalize_carbon_proxy,
)
from src.ui.sidebar import render_sidebar
from src.ui.single_view import render_single_result
from src.ui.compare_view import render_compare_result
from src.ui.kinetics_view import render_kinetics_result


@st.cache_data
def load_data():
    """데이터셋 로딩 (캐시)."""
    return load_dataset()


def _compute_carbon(condition: dict[str, float], dataset_max: float) -> tuple[float, float]:
    """Carbon proxy raw + normalized 계산."""
    raw = compute_carbon_proxy(
        condition["temp_C"],
        condition["time_min"],
        condition["h2so4_M"],
        condition["h2o2_M"],
    )
    normalized = normalize_carbon_proxy(raw, dataset_max)
    return raw, normalized


def main():
    """메인 앱 실행."""
    # 데이터 로딩
    try:
        dataset = load_data()
    except (FileNotFoundError, ValueError) as e:
        st.error(f"❌ 데이터 로딩 실패: {e}")
        st.stop()

    dataset_max = compute_dataset_max_carbon(dataset)
    supported_ranges = compute_supported_ranges(dataset)

    # 사이드바 렌더링
    condition_a, mode, condition_b = render_sidebar()

    # --- 단일 시뮬레이션 ---
    if mode == "single":
        validation = validate_input(condition_a, supported_ranges)
        if not validation.is_valid:
            for err in validation.errors:
                st.error(f"❌ {err}")
            st.stop()

        try:
            result = predict(condition_a, dataset)
            carbon_raw, carbon_norm = _compute_carbon(condition_a, dataset_max)
            render_single_result(result, carbon_norm, carbon_raw)
        except Exception as e:
            st.error(f"❌ 시뮬레이션 오류: {e}")

    # --- 조건 비교 ---
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
            _, carbon_a = _compute_carbon(condition_a, dataset_max)
            _, carbon_b = _compute_carbon(condition_b, dataset_max)
            tradeoff = generate_tradeoff_summary(result_a, result_b, carbon_a, carbon_b)
            render_compare_result(result_a, result_b, carbon_a, carbon_b, tradeoff)
        except Exception as e:
            st.error(f"❌ 비교 시뮬레이션 오류: {e}")

    # --- Kinetics ---
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

            # 시작/종료 탄소 부담
            _, carbon_start = _compute_carbon(
                {**condition_a, "time_min": 1.0}, dataset_max
            )
            _, carbon_end = _compute_carbon(
                {**condition_a, "time_min": 360.0}, dataset_max
            )

            render_kinetics_result(
                kinetics_df, saturation_note, condition_a,
                carbon_start, carbon_end,
            )
        except Exception as e:
            st.error(f"❌ Kinetics 분석 오류: {e}")


if __name__ == "__main__":
    main()
