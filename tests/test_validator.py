"""Unit tests for src/data/validator.py."""

from src.data.validator import compute_supported_ranges, validate_input
from src.data.loader import load_dataset
from src.models import SupportedRange


def _make_ranges():
    return {
        "temp_C": SupportedRange(10.0, 90.0),
        "time_min": SupportedRange(1.0, 360.0),
        "h2so4_M": SupportedRange(0.3, 2.0),
        "h2o2_M": SupportedRange(0.0, 1.96),
        "pulp_density_gL": SupportedRange(20.0, 333.0),
    }


def test_valid_input():
    inputs = {"temp_C": 50.0, "time_min": 60.0, "h2so4_M": 1.0, "h2o2_M": 0.5, "pulp_density_gL": 100.0}
    result = validate_input(inputs, _make_ranges())
    assert result.is_valid
    assert result.errors == []
    assert result.warnings == []


def test_negative_input():
    inputs = {"temp_C": -10.0, "time_min": 60.0, "h2so4_M": 1.0, "h2o2_M": 0.5, "pulp_density_gL": 100.0}
    result = validate_input(inputs, _make_ranges())
    assert not result.is_valid
    assert any("음수" in e for e in result.errors)


def test_out_of_range_warning():
    inputs = {"temp_C": 100.0, "time_min": 60.0, "h2so4_M": 1.0, "h2o2_M": 0.5, "pulp_density_gL": 100.0}
    result = validate_input(inputs, _make_ranges())
    assert result.is_valid  # warnings don't block
    assert any("벗어납니다" in w for w in result.warnings)


def test_compute_supported_ranges():
    df = load_dataset()
    ranges = compute_supported_ranges(df)
    assert "temp_C" in ranges
    assert ranges["temp_C"].min_val == 10.0
    assert ranges["temp_C"].max_val == 90.0
