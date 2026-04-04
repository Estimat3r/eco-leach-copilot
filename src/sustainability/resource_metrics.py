"""개별 burden 계산 (heating / acid / h2o2)."""

HEATING_FACTOR = 0.001
ACID_CARBON_FACTOR = 0.5
H2O2_CARBON_FACTOR = 0.3


def compute_heating_burden(temp_C: float, time_min: float) -> float:
    """(temp_C - 25) × time_min × HEATING_FACTOR. 온도 25°C 미만이면 0."""
    delta = max(temp_C - 25, 0.0)
    return delta * time_min * HEATING_FACTOR


def compute_acid_burden(h2so4_M: float) -> float:
    """h2so4_M × ACID_CARBON_FACTOR."""
    return h2so4_M * ACID_CARBON_FACTOR


def compute_h2o2_burden(h2o2_M: float) -> float:
    """h2o2_M × H2O2_CARBON_FACTOR."""
    return h2o2_M * H2O2_CARBON_FACTOR
