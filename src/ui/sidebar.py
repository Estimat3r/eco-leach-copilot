"""Streamlit 사이드바 입력 폼 (슬라이더 + 모드 선택 + Preset)."""

from __future__ import annotations

import json
import streamlit as st


def _load_presets() -> list[dict]:
    """preset_scenarios.json 로딩."""
    try:
        with open("data/demo/preset_scenarios.json", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("scenarios", [])
    except Exception:
        return []


def _render_condition_sliders(
    prefix: str = "",
    defaults: dict | None = None,
) -> dict[str, float]:
    """공정 조건 슬라이더 렌더링."""
    d = defaults or {}
    condition = {
        "temp_C": st.slider(
            f"{prefix}온도 (°C)", 10, 90,
            int(d.get("temp_C", 60)), key=f"{prefix}temp_C",
        ),
        "time_min": st.slider(
            f"{prefix}반응 시간 (min)", 1, 360,
            int(d.get("time_min", 120)), key=f"{prefix}time_min",
        ),
        "h2so4_M": st.slider(
            f"{prefix}H₂SO₄ 농도 (M)", 0.3, 2.0,
            float(d.get("h2so4_M", 1.0)), step=0.01, key=f"{prefix}h2so4_M",
        ),
        "h2o2_M": st.slider(
            f"{prefix}H₂O₂ 농도 (M)", 0.0, 2.0,
            float(d.get("h2o2_M", 0.5)), step=0.01, key=f"{prefix}h2o2_M",
        ),
        "pulp_density_gL": st.slider(
            f"{prefix}고액비 (g/L)", 20, 333,
            int(d.get("pulp_density_gL", 100)), key=f"{prefix}pulp_density_gL",
        ),
    }
    return {k: float(v) for k, v in condition.items()}


def render_sidebar() -> tuple[dict, str, dict | None]:
    """Streamlit 사이드바 렌더링.

    Returns:
        (input_conditions, mode, condition_b)
        - mode: "single" | "compare" | "kinetics"
        - condition_b: compare 모드일 때 조건 B (그 외 None)
    """
    with st.sidebar:
        st.title("🔋 에코리치")
        st.caption("NCM811 침출 공정 시뮬레이터")
        st.divider()

        # 모드 선택
        mode_labels = {
            "단일 시뮬레이션": "single",
            "조건 비교": "compare",
            "Kinetics": "kinetics",
        }
        mode_display = st.radio(
            "시뮬레이션 모드", list(mode_labels.keys()), index=0
        )
        mode = mode_labels[mode_display]

        st.divider()

        # Preset 선택
        presets = _load_presets()
        preset_names = ["직접 입력"] + [p["name_ko"] for p in presets]
        selected_preset = st.selectbox("📋 프리셋 시나리오", preset_names)

        defaults = None
        if selected_preset != "직접 입력":
            for p in presets:
                if p["name_ko"] == selected_preset:
                    defaults = p["condition"]
                    st.info(f"ℹ️ {p['description_ko']}")
                    break

        st.divider()

        # 조건 입력
        if mode == "compare":
            st.subheader("조건 A")
            condition_a = _render_condition_sliders("A_", defaults)
            st.divider()
            st.subheader("조건 B")
            condition_b = _render_condition_sliders("B_")
            return condition_a, mode, condition_b
        else:
            st.subheader("공정 조건 입력")
            condition = _render_condition_sliders("", defaults)
            return condition, mode, None
