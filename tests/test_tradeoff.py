"""Trade-off 해석 테스트 (CarbonBreakdown 기반)."""

from src.engine.tradeoff import generate_tradeoff_summary
from src.models import PredictionResult
from src.sustainability.carbon_emission import CarbonBreakdown


def _make_result(li, ni, co, mn):
    return PredictionResult(
        leach_rates={"Li_pct": li, "Ni_pct": ni, "Co_pct": co, "Mn_pct": mn},
        confidence_tier="high",
        nearest_distance=0.05,
        prediction_mode="exact",
        warnings=[],
    )


def _make_carbon(total):
    return CarbonBreakdown(heating_kg=total * 0.6, acid_kg=total * 0.2, h2o2_kg=total * 0.2, total_kg=total)


def test_tradeoff_not_empty():
    a = _make_result(80, 70, 75, 60)
    b = _make_result(90, 85, 88, 75)
    summary = generate_tradeoff_summary(a, b, _make_carbon(0.01), _make_carbon(0.03))
    assert len(summary) > 0


def test_tradeoff_contains_keywords():
    a = _make_result(90, 85, 88, 75)
    b = _make_result(80, 70, 75, 60)
    summary = generate_tradeoff_summary(a, b, _make_carbon(0.03), _make_carbon(0.01))
    assert "회수율" in summary or "탄소" in summary


def test_tradeoff_lower_recovery_lower_carbon():
    a = _make_result(90, 85, 88, 75)
    b = _make_result(80, 70, 75, 60)
    summary = generate_tradeoff_summary(a, b, _make_carbon(0.03), _make_carbon(0.01))
    assert "낮지만" in summary or "적습니다" in summary
