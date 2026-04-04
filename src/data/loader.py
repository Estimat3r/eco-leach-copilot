"""CSV 데이터셋 로딩 및 검증."""

import pandas as pd

from src.data.schema import COLUMN_TYPES, REQUIRED_COLUMNS


def load_dataset(filepath: str = "data/csv/ncm811_dataset.csv") -> pd.DataFrame:
    """CSV 파일을 로딩하고 필수 컬럼 검증 후 DataFrame 반환.

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때
        ValueError: 필수 컬럼이 누락되었을 때 (누락 컬럼명 포함)
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {filepath}")

    # 필수 컬럼 검증
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"필수 컬럼이 누락되었습니다: {missing}")

    # 빈 DataFrame 검증
    if df.empty:
        raise ValueError("데이터셋이 비어있습니다")

    # float 타입 변환
    for col, dtype in COLUMN_TYPES.items():
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 변환 실패 행 제거
    df = df.dropna(subset=REQUIRED_COLUMNS)

    return df
