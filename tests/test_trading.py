"""
Test the functions in pairs_trading_oaf/trading.py
"""
from unittest.mock import patch
import pandas as pd
import pytest
import pairs_trading_oaf.trading as trading

# Sample data for mocking
mocked_stock_a_data = pd.DataFrame({'Close': [100.0, 105.0, 95.0, 110.0, 90.0]})
mocked_stock_b_data = pd.DataFrame({'Close': [200.0, 210.0, 190.0, 220.0, 180.0]})

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
    mock_download.side_effect = stock_data_side_effect
    sample_portfolio.calculate_trading_thresholds("2020-01-01", "2020-12-31")
    assert sample_portfolio.long_stock_a_threshold is not None
    assert sample_portfolio.long_stock_b_threshold is not None
    # More detailed checks can be added here

@patch("pairs_trading_oaf.trading.yf.download")
def test_execute_trades(mock_download, sample_portfolio):
    """
    Test the execution of trades.
    """
    mock_download.side_effect = stock_data_side_effect
    sample_portfolio.calculate_trading_thresholds("2020-01-01", "2020-12-31")
    sample_portfolio.execute_trades("2021-01-01", "2021-12-31")
    assert sample_portfolio.trading_start_date == "2021-01-01"
    assert sample_portfolio.trading_end_date == "2021-12-31"
    assert 1 == 1
    # More assertions on portfolio state after trade execution

@patch("pairs_trading_oaf.trading.yf.download")
def test_run_pairs_trade_strategy(mock_download):
    """
    Test the run_pairs_trade_strategy function.
    """
    mock_download.side_effect = stock_data_side_effect
    portfolio = trading.run_pairs_trade_strategy()
    assert isinstance(portfolio, trading.Portfolio)
    # Additional checks for the state of the portfolio
