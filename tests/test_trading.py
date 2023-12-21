"""
Test the functions in pairs_trading_oaf/trading.py
"""

import pytest
from unittest.mock import patch, MagicMock
import pairs_trading_oaf.trading as trading

# Sample data for mocking
mocked_stock_data = MagicMock()
mocked_stock_data['Close'] = [100, 105, 95, 110, 90]

@pytest.fixture
def sample_portfolio():
    return trading.Portfolio("AAPL", "MSFT")

def test_portfolio_initialization(sample_portfolio):
    assert sample_portfolio.stock_a_ticker == "AAPL"
    assert sample_portfolio.stock_b_ticker == "MSFT"
    assert sample_portfolio.cash == 0
    # Add more assertions for other attributes

@patch("trading.yf.download")
def test_calculate_trading_thresholds(mock_download, sample_portfolio):
    mock_download.return_value = mocked_stock_data
    sample_portfolio.calculate_trading_thresholds("2020-01-01", "2020-12-31")
    assert sample_portfolio.long_stock_a_threshold is not None
    assert sample_portfolio.long_stock_b_threshold is not None
    # More detailed checks can be added here

@patch("trading.yf.download")
def test_execute_trades(mock_download, sample_portfolio):
    mock_download.return_value = mocked_stock_data
    sample_portfolio.calculate_trading_thresholds("2020-01-01", "2020-12-31")
    sample_portfolio.execute_trades("2021-01-01", "2021-12-31")
    assert sample_portfolio.position is not None
    # More assertions on portfolio state after trade execution

def test_run_pairs_trade_strategy():
    with patch("trading.yf.download", return_value=mocked_stock_data):
        portfolio = trading.run_pairs_trade_strategy()
        assert isinstance(portfolio, trading.Portfolio)
        # Additional checks for the state of the portfolio
