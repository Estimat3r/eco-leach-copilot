"""Unit tests for src/engine/predictor.py."""

from src.data.loader import load_dataset
from src.data.schema import OUTPUT_COLUMNS
from src.engine.predictor import predict


def test_predict_returns_all_metals():
    df = load_dataset()
    condition = {"temp_C": 50.0, "time_min": 60.0, "h2so4_M": 1.0, "h2o2_M": 0.5, "pulp_density_gL": 100.0}
    result = predict(condition, df)
    assert set(result.leach_rates.keys()) == set(OUTPUT_COLUMNS)
    for v in result.leach_rates.values():
        assert 0.0 <= v <= 100.0


def test_predict_exact_match():
    """데이터셋 행을 그대로 입력하면 exact 모드."""
    df = load_dataset()
    row = df.iloc[0]
    condition = {col: float(row[col]) for col in ["temp_C", "time_min", "h2so4_M", "h2o2_M", "pulp_density_gL"]}
    result = predict(condition, df)
    assert result.prediction_mode == "exact"
    assert result.confidence_tier == "high"


def test_predict_confidence_tier_valid():
    df = load_dataset()
    condition = {"temp_C": 50.0, "time_min": 60.0, "h2so4_M": 1.0, "h2o2_M": 0.5, "pulp_density_gL": 100.0}
    result = predict(condition, df)
    assert result.confidence_tier in ("high", "medium", "low")
    assert result.prediction_mode in ("exact", "interpolation", "extrapolation")
