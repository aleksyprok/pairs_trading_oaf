"""
Test routines for the pairs_trading_oaf.data module.
"""

import pytest
import pandas as pd
from pairs_trading_oaf import data  # Replace with your actual module import

@pytest.fixture
def mock_csv(tmp_path):
    """
    Create a mock CSV file for testing.
    """
    df = pd.DataFrame({
        'Closing Date': pd.date_range(start='2021-01-01', periods=5, freq='D'),
        'SomeColumnName': [100, 200, 300, 400, 500]
    })
    df.set_index('Closing Date', inplace=True)

    csv_file = tmp_path / "mock_data.csv"
    df.to_csv(csv_file)
    return csv_file

# pylint: disable=redefined-outer-name
def test_read_csv_correct_file_reading(mock_csv):
    """
    Test whether the function reads the correct file.
    """
    df = data.read_csv(str(mock_csv))
    assert isinstance(df, pd.DataFrame), "The function should return a pandas DataFrame."

# pylint: disable=redefined-outer-name
def test_read_csv_index_check(mock_csv):
    """
    Test whether the function sets the index correctly.
    """
    df = data.read_csv(str(mock_csv))
    assert df.index.name == 'Closing Date', "Index should be set to 'Closing Date'."
    assert pd.api.types.is_datetime64_any_dtype(df.index), "Index should be datetime type."

# pylint: disable=redefined-outer-name
def test_read_csv_file_not_found():
    """
    Test whether the function raises an error when the file is not found.
    """
    with pytest.raises(FileNotFoundError):
        data.read_csv("nonexistent_file.csv")

# pylint: disable=redefined-outer-name
def test_read_csv_content_check(mock_csv):
    """
    Test whether the function reads the correct content.
    """
    df = data.read_csv(str(mock_csv))
    assert 'SomeColumnName' in df.columns, "DataFrame should have a specific column."
    assert len(df) > 0, "DataFrame should not be empty."
