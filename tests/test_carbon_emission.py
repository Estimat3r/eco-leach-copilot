"""탄소 배출량 계산 테스트."""

from src.sustainability.carbon_emission import (
    compute_carbon_emission,
    generate_reduction_recommendations,
)


def test_total_is_sum_of_components():
    result = compute_carbon_emission(75, 120, 1.0, 0.5)
    assert abs(result.total_kg - (result.heating_kg + result.acid_kg + result.h2o2_kg)) < 1e-10


def test_higher_temp_more_emission():
    low = compute_carbon_emission(40, 120, 1.0, 0.5)
    high = compute_carbon_emission(80, 120, 1.0, 0.5)
    assert high.total_kg > low.total_kg


def test_no_heating_at_25c():
    result = compute_carbon_emission(25, 120, 1.0, 0.5)
    assert result.heating_kg == 0.0


def test_percentages_sum_to_100():
    result = compute_carbon_emission(75, 120, 1.0, 0.5)
    total_pct = result.heating_pct + result.acid_pct + result.h2o2_pct
    assert abs(total_pct - 100.0) < 0.1


def test_recommendations_not_empty():
    result = compute_carbon_emission(75, 120, 1.0, 0.5)
    recs = generate_reduction_recommendations(result, 75, 120, 1.0, 0.5)
    assert len(recs) > 0


def test_more_h2o2_more_emission():
    low = compute_carbon_emission(60, 60, 1.0, 0.2)
    high = compute_carbon_emission(60, 60, 1.0, 1.5)
    assert high.h2o2_kg > low.h2o2_kg
