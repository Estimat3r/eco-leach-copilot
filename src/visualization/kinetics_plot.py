"""시간축 금속별 침출률 line plot (Plotly)."""

import pandas as pd
import plotly.graph_objects as go


METAL_COLORS = {
    "Li_pct": ("#636EFA", "Li"),   # 파랑
    "Ni_pct": ("#00CC96", "Ni"),   # 초록
    "Co_pct": ("#EF553B", "Co"),   # 주황
    "Mn_pct": ("#AB63FA", "Mn"),   # 보라
}


def create_kinetics_line_plot(kinetics_data: pd.DataFrame) -> go.Figure:
    """시간축 금속별 침출률 line plot 생성 (Plotly).

    Args:
        kinetics_data: columns = [time_min, Li_pct, Ni_pct, Co_pct, Mn_pct]

    Returns:
        Plotly Figure
    """
    fig = go.Figure()

    for col, (color, name) in METAL_COLORS.items():
        if col in kinetics_data.columns:
            fig.add_trace(go.Scatter(
                x=kinetics_data["time_min"],
                y=kinetics_data[col],
                mode="lines+markers",
                name=name,
                line=dict(color=color, width=2),
                marker=dict(size=5),
            ))

    fig.update_layout(
        title="시간에 따른 금속별 침출률 변화",
        xaxis_title="반응 시간 (min)",
        yaxis_title="침출률 (%)",
        yaxis_range=[0, 105],
        template="plotly_white",
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    return fig
