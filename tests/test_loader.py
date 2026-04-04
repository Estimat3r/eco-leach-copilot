"""Unit tests for src/data/loader.py."""

import pandas as pd
import pytest

from src.data.loader import load_dataset
from src.data.schema import REQUIRED_COLUMNS


def test_load_dataset_success():
    """실제 CSV 파일 로딩 성공."""
    df = load_dataset()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    for col in REQUIRED_COLUMNS:
        assert col in df.columns
        assert df[col].dtype == float


def test_load_dataset_file_not_found():
    """존재하지 않는 파일 경로."""
    with pytest.raises(FileNotFoundError, match="데이터 파일을 찾을 수 없습니다"):
        load_dataset("nonexistent.csv")


def test_load_dataset_missing_columns(tmp_path):
    """필수 컬럼 누락 시 ValueError."""
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text("temp_C,time_min\n10,1\n")
    with pytest.raises(ValueError, match="필수 컬럼이 누락되었습니다"):
        load_dataset(str(csv_file))


def test_load_dataset_all_columns_float():
    """로딩 후 모든 컬럼이 float 타입."""
    df = load_dataset()
    for col in REQUIRED_COLUMNS:
        assert df[col].dtype == float
