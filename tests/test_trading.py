"""
Test the functions in pairs_trading_oaf/trading.py
"""
from unittest.mock import patch
import numpy as np
import pandas as pd
import pytest
import pairs_trading_oaf.trading as trading

# Sample data for mocking
mocked_stock_a_data = pd.DataFrame({'Close': [100.0, 105.0, 95.0, 110.0, 90.0]})
mocked_stock_b_data = pd.DataFrame({'Close': [200.0, 175.0, 190.0, 275.0, 180.0]})
# ratio = [0.5, 0.6, 0.5, 0.4, 0.5]
# mean = 0.5
# std = 0.0707107

def stock_data_side_effect(ticker, start=None, end=None): # pylint: disable=unused-argument
    """
    Side effect for mocking yfinance.download.
    """
    if ticker == "AAPL":
        return mocked_stock_a_data
    elif ticker == "MSFT":
        return mocked_stock_b_data
    raise ValueError("Unknown ticker")

@pytest.fixture(name="sample_portfolio")
def fixture_sample_portfolio():
    """
    Create a sample portfolio object.
    """
    return trading.Portfolio("AAPL", "MSFT")

def test_portfolio_initialization(sample_portfolio):
    """
    Test the initialization of the Portfolio class and its attributes.
    """
    assert sample_portfolio.stock_a_ticker == "AAPL"
    assert sample_portfolio.stock_b_ticker == "MSFT"
    assert sample_portfolio.cash == 0
    assert sample_portfolio.stock_a == 0
    assert sample_portfolio.stock_b == 0
    assert sample_portfolio.position is None
    assert sample_portfolio.position_limit == 1000000
    assert sample_portfolio.long_stock_a_threshold is None
    assert sample_portfolio.long_stock_b_threshold is None
    assert sample_portfolio.cash_over_time == []
    assert sample_portfolio.stock_a_over_time == []
    assert sample_portfolio.stock_b_over_time == []
    assert sample_portfolio.position_over_time == []
    assert sample_portfolio.trading_start_date is None
    assert sample_portfolio.trading_end_date is None
    assert len(sample_portfolio.__dict__) == 15

@patch("pairs_trading_oaf.trading.yf.download")
def test_calculate_trading_thresholds(mock_download, sample_portfolio):
    """
    Test the calculation of trading thresholds.
    """
    # Arrange
    mock_download.side_effect = stock_data_side_effect
    # expected_ratio = [0.5, 0.6, 0.5, 0.4, 0.5]
    expected_mean = 0.5
    expected_std = 0.0707107
    expected_long_stock_a_threshold = expected_mean - 0.5 * expected_std
    expected_long_stock_b_threshold = expected_mean + 0.5 * expected_std

    # Act
    sample_portfolio.calculate_trading_thresholds("2020-01-01", "2020-12-31")

    # Assert
    assert np.isclose(sample_portfolio.long_stock_a_threshold, expected_long_stock_a_threshold)
    assert np.isclose(sample_portfolio.long_stock_b_threshold, expected_long_stock_b_threshold)

@patch("pairs_trading_oaf.trading.yf.download")
def test_execute_trades(mock_download, sample_portfolio):
    """
    Test the execution of trades in the Portfolio.
    """
    # Arrange
    mock_download.side_effect = stock_data_side_effect
    sample_portfolio.calculate_trading_thresholds("2020-01-01", "2020-12-31")

    # Act
    sample_portfolio.execute_trades("2021-01-01", "2021-12-31")

    # Assert
    assert sample_portfolio.trading_start_date == "2021-01-01"
    assert sample_portfolio.trading_end_date == "2021-12-31"
    # ratio over time = [0.5, 0.6, 0.5, 0.4, 0.5]
    # stock_a_prices = [100.0, 105.0, 95.0, 110.0, 90.0]
    # stock_b_prices = [200.0, 175.0, 190.0, 275.0, 180.0]
    assert sample_portfolio.position_over_time == [None,
                                                   'short A long B',
                                                   'short A long B',
                                                   'long A short B',
                                                   'long A short B']
    assert np.allclose(sample_portfolio.stock_a_over_time,
                       [0,
                        -sample_portfolio.position_limit / 105.0,
                        -sample_portfolio.position_limit / 105.0,
                        +sample_portfolio.position_limit / 110.0,
                        +sample_portfolio.position_limit / 110.0])
    assert np.allclose(sample_portfolio.stock_b_over_time,
                       [0,
                        +sample_portfolio.position_limit / 175.0,
                        +sample_portfolio.position_limit / 175.0,
                        -sample_portfolio.position_limit / 275.0,
                        -sample_portfolio.position_limit / 275.0])
    cash = sample_portfolio.stock_a_over_time[2] * 110.0 \
         + sample_portfolio.stock_b_over_time[2] * 275.0
    assert np.allclose(sample_portfolio.cash_over_time,
                       [0, 0, 0, cash, cash])