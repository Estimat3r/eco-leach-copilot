"""조건 비교 차트 (Plotly grouped bar)."""

import plotly.graph_objects as go


METAL_NAMES = {
    "Li_pct": "Li",
    "Ni_pct": "Ni",
    "Co_pct": "Co",
    "Mn_pct": "Mn",
}


def create_comparison_bar_chart(
    result_a: dict[str, float],
    result_b: dict[str, float],
    labels: tuple[str, str] = ("조건 A", "조건 B"),
) -> go.Figure:
    """금속별 침출률 grouped bar chart 생성 (Plotly)."""
    metals = list(METAL_NAMES.values())
    keys = list(METAL_NAMES.keys())

    values_a = [result_a.get(k, 0.0) for k in keys]
    values_b = [result_b.get(k, 0.0) for k in keys]

    fig = go.Figure(data=[
        go.Bar(
            name=labels[0], x=metals, y=values_a,
            marker_color="#636EFA", text=[f"{v:.1f}%" for v in values_a],
            textposition="auto",
        ),
        go.Bar(
            name=labels[1], x=metals, y=values_b,
            marker_color="#EF553B", text=[f"{v:.1f}%" for v in values_b],
            textposition="auto",
        ),
    ])

    fig.update_layout(
        title="금속별 침출률 비교",
        xaxis_title="금속",
        yaxis_title="침출률 (%)",
        yaxis_range=[0, 105],
        barmode="group",
        template="plotly_white",
        height=400,
    )
    return fig


def create_carbon_comparison_bar(
    carbon_a: float,
    carbon_b: float,
    labels: tuple[str, str] = ("조건 A", "조건 B"),
) -> go.Figure:
    """Carbon Proxy Index 비교 바 차트 생성 (Plotly)."""
    fig = go.Figure(data=[
        go.Bar(
            x=[labels[0], labels[1]],
            y=[carbon_a, carbon_b],
            marker_color=["#636EFA", "#EF553B"],
            text=[f"{carbon_a:.3f}", f"{carbon_b:.3f}"],
            textposition="auto",
        ),
    ])

    fig.update_layout(
        title="🌱 Carbon Proxy Index 비교",
        yaxis_title="Carbon Proxy (정규화)",
        yaxis_range=[0, max(carbon_a, carbon_b, 0.1) * 1.2],
        template="plotly_white",
        height=300,
    )
    return fig
