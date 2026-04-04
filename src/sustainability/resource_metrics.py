"""실제 LCA emission factor 기반 탄소 배출량 계산 (kg CO₂).

참조:
- 한국 전력 grid emission factor: 0.459 kg CO₂/kWh (환경부 2022)
- H₂SO₄ 생산: ~0.09 kg CO₂/kg (ecoinvent, contact process)
- H₂O₂ 생산: ~2.5 kg CO₂/kg (anthraquinone process, Thunder Said Energy)
- 물 비열: 4.186 kJ/(kg·°C)
- 전기 가열 효율: 90%
- 열 유지 손실: 가열 에너지의 15% × (time_min / 60)
"""

# === Emission Factors ===
GRID_EMISSION_FACTOR = 0.459       # kg CO₂/kWh (한국 2022)
H2SO4_EMISSION_FACTOR = 0.09      # kg CO₂/kg H₂SO₄
H2O2_EMISSION_FACTOR = 2.5        # kg CO₂/kg H₂O₂

# === Physical Constants ===
WATER_CP = 4.186                   # kJ/(kg·°C)
HEATING_EFFICIENCY = 0.90          # 전기 가열 효율
HEAT_LOSS_RATE = 0.15              # 시간당 열 유지 손실 비율

# === Molecular Weights ===
MW_H2SO4 = 0.098                   # kg/mol
MW_H2O2 = 0.034                    # kg/mol

# === Default Assumptions ===
DEFAULT_VOLUME_L = 1.0             # 기본 반응 용액 부피 (L)


def compute_heating_emission(
    temp_C: float,
    time_min: float,
    volume_L: float = DEFAULT_VOLUME_L,
) -> float:
    """가열 에너지에 의한 CO₂ 배출량 (kg CO₂).

    1) 초기 가열: Q = m × Cp × ΔT
    2) 열 유지: Q_maintain = Q_initial × HEAT_LOSS_RATE × (time_h)
    3) 전기 → CO₂: total_kWh × GRID_EMISSION_FACTOR
    """
    delta_T = max(temp_C - 25.0, 0.0)
    if delta_T == 0:
        return 0.0

    mass_kg = volume_L  # 물 밀도 ≈ 1 kg/L
    Q_initial_kJ = mass_kg * WATER_CP * delta_T
    Q_initial_kWh = Q_initial_kJ / 3600.0 / HEATING_EFFICIENCY

    time_h = time_min / 60.0
    Q_maintain_kWh = Q_initial_kWh * HEAT_LOSS_RATE * time_h

    total_kWh = Q_initial_kWh + Q_maintain_kWh
    return total_kWh * GRID_EMISSION_FACTOR


def compute_acid_emission(
    h2so4_M: float,
    volume_L: float = DEFAULT_VOLUME_L,
) -> float:
    """H₂SO₄ 생산에 의한 CO₂ 배출량 (kg CO₂)."""
    mass_kg = h2so4_M * MW_H2SO4 * volume_L
    return mass_kg * H2SO4_EMISSION_FACTOR


def compute_h2o2_emission(
    h2o2_M: float,
    volume_L: float = DEFAULT_VOLUME_L,
) -> float:
    """H₂O₂ 생산에 의한 CO₂ 배출량 (kg CO₂)."""
    mass_kg = h2o2_M * MW_H2O2 * volume_L
    return mass_kg * H2O2_EMISSION_FACTOR
