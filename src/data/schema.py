"""데이터셋 스키마 정의: 필수 컬럼, 타입 매핑, 입력/출력 컬럼 분류."""

REQUIRED_COLUMNS = [
    "temp_C", "time_min", "h2so4_M", "h2o2_M", "pulp_density_gL",
    "Li_pct", "Ni_pct", "Co_pct", "Mn_pct",
]

COLUMN_TYPES = {col: float for col in REQUIRED_COLUMNS}

INPUT_COLUMNS = ["temp_C", "time_min", "h2so4_M", "h2o2_M", "pulp_density_gL"]

OUTPUT_COLUMNS = ["Li_pct", "Ni_pct", "Co_pct", "Mn_pct"]
