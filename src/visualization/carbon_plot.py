"""탄소 배출량 시각화 (Plotly)."""

import plotly.graph_objects as go

from src.sustainability.carbon_emission import CarbonBreakdown


def create_carbon_breakdown_pie(breakdown: CarbonBreakdown) -> go.Figure:
    """탄소 배출 분해 파이 차트."""
    labels = ["가열 에너지", "H₂SO₄ 생산", "H₂O₂ 생산"]
    values = [breakdown.heating_kg, breakdown.acid_kg, breakdown.h2o2_kg]
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1"]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        textinfo="label+percent",
        texttemplate="%{label}<br>%{value:.4f} kg<br>(%{percent})",
        hole=0.4,
    )])
    fig.update_layout(
        title="탄소 배출 구성 분석",
        template="plotly_white",
        height=350,
        showlegend=False,
    )
    return fig


def create_carbon_comparison_grouped(
    breakdown_a: CarbonBreakdown,
    breakdown_b: CarbonBreakdown,
) -> go.Figure:
    """두 조건의 탄소 배출 분해 비교 grouped bar."""
    categories = ["가열 에너지", "H₂SO₄", "H₂O₂", "합계"]
    vals_a = [breakdown_a.heating_kg, breakdown_a.acid_kg, breakdown_a.h2o2_kg, breakdown_a.total_kg]
    vals_b = [breakdown_b.heating_kg, breakdown_b.acid_kg, breakdown_b.h2o2_kg, breakdown_b.total_kg]

    fig = go.Figure(data=[
        go.Bar(name="조건 A", x=categories, y=vals_a,
               marker_color="#636EFA",
               text=[f"{v:.4f}" for v in vals_a], textposition="auto"),
        go.Bar(name="조건 B", x=categories, y=vals_b,
               marker_color="#EF553B",
               text=[f"{v:.4f}" for v in vals_b], textposition="auto"),
    ])
    fig.update_layout(
        title="조건별 탄소 배출량 비교 (kg CO₂)",
        yaxis_title="kg CO₂",
        barmode="group",
        template="plotly_white",
        height=400,
    )
    return fig
