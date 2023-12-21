"""
Test the functions in pairs_trading_oaf/trading.py
"""
from unittest.mock import patch, MagicMock
import pytest
import pairs_trading_oaf.trading as trading

# Sample data for mocking
mocked_stock_data = MagicMock()
mocked_stock_data['Close'] = [100, 105, 95, 110, 90]

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
    # Add more assertions for other attributes

@patch("pairs_trading_oaf.trading.yf.download")
def test_calculate_trading_thresholds(mock_download, sample_portfolio):
    """
    Test the calculation of trading thresholds.
    """
    mock_download.return_value = mocked_stock_data
    sample_portfolio.calculate_trading_thresholds("2020-01-01", "2020-12-31")
    assert sample_portfolio.long_stock_a_threshold is not None
    assert sample_portfolio.long_stock_b_threshold is not None
    # More detailed checks can be added here

@patch("pairs_trading_oaf.trading.yf.download")
def test_execute_trades(mock_download, sample_portfolio):
    """
    Test the execution of trades.
    """
    mock_download.return_value = mocked_stock_data
    sample_portfolio.calculate_trading_thresholds("2020-01-01", "2020-12-31")
    sample_portfolio.execute_trades("2021-01-01", "2021-12-31")
    assert sample_portfolio.trading_start_date is not None
    assert 1 == 1
    # More assertions on portfolio state after trade execution

@patch("pairs_trading_oaf.trading.yf.download", return_value=mocked_stock_data)
def test_run_pairs_trade_strategy(mock_download):
    """
    Test the run_pairs_trade_strategy function.
    """
    portfolio = trading.run_pairs_trade_strategy()
    assert isinstance(portfolio, trading.Portfolio)
    # Additional checks for the state of the portfolio
