"""Unit tests for src/sustainability/carbon_proxy.py."""

from src.data.loader import load_dataset
from src.sustainability.carbon_proxy import (
    compute_carbon_proxy,
    compute_dataset_max_carbon,
    normalize_carbon_proxy,
)
from src.sustainability.resource_metrics import (
    compute_acid_burden,
    compute_h2o2_burden,
    compute_heating_burden,
)


def test_carbon_proxy_decomposition():
    """Carbon proxy = heating + acid + h2o2 burden 합산."""
    t, tm, acid, h2o2 = 60.0, 120.0, 1.5, 0.8
    expected = compute_heating_burden(t, tm) + compute_acid_burden(acid) + compute_h2o2_burden(h2o2)
    assert abs(compute_carbon_proxy(t, tm, acid, h2o2) - expected) < 1e-10


def test_normalize_range():
    assert normalize_carbon_proxy(5.0, 10.0) == 0.5
    assert normalize_carbon_proxy(0.0, 10.0) == 0.0
    assert normalize_carbon_proxy(10.0, 10.0) == 1.0


def test_normalize_zero_max():
    assert normalize_carbon_proxy(5.0, 0.0) == 0.0


def test_dataset_max_positive():
    df = load_dataset()
    max_val = compute_dataset_max_carbon(df)
    assert max_val > 0


def test_temperature_monotonicity():
    """온도가 높으면 carbon proxy도 높다."""
    cp_low = compute_carbon_proxy(30.0, 60.0, 1.0, 0.5)
    cp_high = compute_carbon_proxy(80.0, 60.0, 1.0, 0.5)
    assert cp_high >= cp_low
