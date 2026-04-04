"""Unit tests for src/engine/confidence.py."""

from src.engine.confidence import compute_confidence_tier, generate_warnings
from src.models import SupportedRange


def test_high_confidence():
    assert compute_confidence_tier(0.05, 5) == "high"


def test_medium_confidence():
    assert compute_confidence_tier(0.2, 3) == "medium"


def test_low_confidence_far():
    assert compute_confidence_tier(0.5, 5) == "low"


def test_low_confidence_few_neighbors():
    assert compute_confidence_tier(0.2, 2) == "low"


def test_generate_warnings_out_of_range():
    ranges = {"temp_C": SupportedRange(10.0, 90.0)}
    warnings = generate_warnings({"temp_C": 100.0}, ranges, 0.1)
    assert any("벗어납니다" in w for w in warnings)


def test_generate_warnings_extrapolation():
    ranges = {"temp_C": SupportedRange(10.0, 90.0)}
    warnings = generate_warnings({"temp_C": 50.0}, ranges, 0.5)
    assert any("신뢰도" in w for w in warnings)
