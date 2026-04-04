"""Unit tests for src/engine/tradeoff.py."""

from src.engine.tradeoff import generate_tradeoff_summary
from src.models import PredictionResult


def _make_result(li=80.0, ni=75.0, co=70.0, mn=65.0, mode="interpolation"):
    return PredictionResult(
        leach_rates={"Li_pct": li, "Ni_pct": ni, "Co_pct": co, "Mn_pct": mn},
        confidence_tier="medium",
        nearest_distance=0.2,
        prediction_mode=mode,
    )


def test_tradeoff_not_empty():
    a = _make_result()
    b = _make_result(li=90.0, ni=85.0, co=80.0, mn=75.0)
    summary = generate_tradeoff_summary(a, b, 2.0, 5.0)
    assert len(summary) > 0


def test_tradeoff_contains_keywords():
    a = _make_result()
    b = _make_result(li=60.0, ni=55.0, co=50.0, mn=45.0)
    summary = generate_tradeoff_summary(a, b, 5.0, 2.0)
    assert "회수율" in summary
    assert "탄소" in summary


def test_tradeoff_lower_recovery_lower_carbon():
    a = _make_result(li=80.0, ni=80.0, co=80.0, mn=80.0)
    b = _make_result(li=60.0, ni=60.0, co=60.0, mn=60.0)
    summary = generate_tradeoff_summary(a, b, 5.0, 2.0)
    assert "낮지만" in summary
    assert "적습니다" in summary
