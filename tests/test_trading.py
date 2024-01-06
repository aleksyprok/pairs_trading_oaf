"""
Test routines for the pairs_trading_oaf.trading module.
"""
from unittest.mock import patch
import numpy as np
import pandas as pd
import pytest
from pairs_trading_oaf import portfolio, trading

class MockStrategy:
    """
    Mock strategy class of the same format as those in the strategies module
    for testing purposes.

    We use a very simple strategy here to make the testing easier.

    If it's the first of the month, we go long on stock A and short on stock B.
    If it's the second of the month, we go long on stock B and short on stock A.
    If it's the third of the month, we hold no position.
    If it's the fourth of the month, we go long on stock A and short on stock B.
    If it's the fifth of the month, we again go long on stock A and short on stock B.
    """
    def __init__(self, pair_portfolio):
        self.pair_portfolio = pair_portfolio

    def calculate_new_position(self):
        """
        Calculate the new position for the pair portfolio. This method needs to be implemented by
        all concrete strategy classes.
        """
        current_date = self.pair_portfolio.date
        if current_date.day == 1:
            return "long A short B"
        elif current_date.day == 2:
            return "long B short A"
        elif current_date.day == 3:
            return "no position"
        elif current_date.day == 4:
            return "long A short B"
        elif current_date.day == 5:
            return "long A short B"
        else:
            raise ValueError("Invalid date")

@pytest.fixture
def master_portfolio():
    """
    Master portfolio for testing purposes.

    We don't need to specify the training and testing data because we are mocking the
    data.read_csv function.
    """
    position_limit = 1
    training_data_str = None
    testing_data_str = None
    mp = portfolio.MasterPortfolio(position_limit, training_data_str, testing_data_str)
    return mp

# pylint: disable=redefined-outer-name
@patch('pairs_trading_oaf.data.read_csv')
def test_simulate_trading(mock_read_csv, master_portfolio):
    """
    Test whether the trading simulation gives the expected results on mock data
    with the mock strategy.
    """

    # Arrange

    # Create a mock CSV file for when we call data.read_csv
    mock_data = pd.DataFrame({'Date': pd.date_range(start='2021-01-01', periods=5, freq='D'),
                              'StockA': [100, 101, 102, 103, 104],
                              'StockB': [200, 201, 202, 203, 204],
                              'StockC': [300, 301, 302, 303, 304],
                              'StockD': [400, 401, 402, 403, 404]
                             })
    mock_data.index = mock_data['Date']
    mock_read_csv.return_value = mock_data

    # Add two mock pair portfolios to the master portfolio.
    pair_portfolio1 = portfolio.PairPortfolio(('StockA', 'StockB'), MockStrategy, master_portfolio)
    pair_portfolio2 = portfolio.PairPortfolio(('StockD', 'StockC'), MockStrategy, master_portfolio)
    master_portfolio.add_pair_portfolio(pair_portfolio1)
    master_portfolio.add_pair_portfolio(pair_portfolio2)

    # Act
    trading.simulate_trading(master_portfolio)

    # Assertions
    assert len(master_portfolio.pair_portfolios) == 2
    assert master_portfolio.pair_portfolios[0].stock_pair_labels == ('StockA', 'StockB')
    assert master_portfolio.pair_portfolios[1].stock_pair_labels == ('StockD', 'StockC')
    assert master_portfolio.pair_portfolios[0].position_over_time == \
        ['long A short B', 'long B short A', 'no position', 'long A short B', 'long A short B']
    assert master_portfolio.pair_portfolios[1].position_over_time == \
        ['long A short B', 'long B short A', 'no position', 'long A short B', 'long A short B']
    expected_shares_over_time = [(+1 / 100, -1 / 200),
                                 (-1 / 101, +1 / 201),
                                 (0, 0),
                                 (+1 / 103, -1 / 203),
                                 (+1 / 103, -1 / 203)]
    actual_shares_over_time = master_portfolio.pair_portfolios[0].shares_over_time
    for actual, expected in zip(actual_shares_over_time, expected_shares_over_time):
        assert actual[0] == pytest.approx(expected[0])
        assert actual[1] == pytest.approx(expected[1])
    expected_shares_over_time = [(+1 / 400, -1 / 300),
                                 (-1 / 401, +1 / 301),
                                 (0, 0),
                                 (+1 / 403, -1 / 303),
                                 (+1 / 403, -1 / 303)]
    actual_shares_over_time = master_portfolio.pair_portfolios[1].shares_over_time
    for actual, expected in zip(actual_shares_over_time, expected_shares_over_time):
        assert actual[0] == pytest.approx(expected[0])
        assert actual[1] == pytest.approx(expected[1])
    actual_cash_over_time = master_portfolio.pair_portfolios[0].cash_over_time
    cash_changes_over_time = [0,
                              +1 / 100 * 101 - 1 / 200 * 201,
                              -1 / 101 * 102 + 1 / 201 * 202,
                              0,
                              0]
    excepted_cash_over_time = np.cumsum(cash_changes_over_time)
    for actual, expected in zip(actual_cash_over_time, excepted_cash_over_time):
        assert actual == pytest.approx(expected)
    actual_cash_over_time = master_portfolio.pair_portfolios[1].cash_over_time
    cash_changes_over_time = [0,
                              +1 / 400 * 401 - 1 / 300 * 301,
                              -1 / 401 * 402 + 1 / 301 * 302,
                              0,
                              0]
    excepted_cash_over_time = np.cumsum(cash_changes_over_time)
    for actual, expected in zip(actual_cash_over_time, excepted_cash_over_time):
        assert actual == pytest.approx(expected)
    assert master_portfolio.pair_portfolios[0].stock_pair_prices_over_time == \
        [(100, 200), (101, 201), (102, 202), (103, 203), (104, 204)]
    assert master_portfolio.pair_portfolios[1].stock_pair_prices_over_time == \
        [(400, 300), (401, 301), (402, 302), (403, 303), (404, 304)]

# pylint: disable=redefined-outer-name
def test_close_position(master_portfolio):
    """
    Test the close_position function.
    """
    # Setup
    pair_portfolio = portfolio.PairPortfolio(('StockA', 'StockB'), MockStrategy, master_portfolio)
    pair_portfolio.shares = (10, -5)
    pair_portfolio.stock_pair_prices = (100, 200)
    pair_portfolio.cash = 1000

    # Action
    trading.close_position(pair_portfolio)

    # Assertions
    expected_cash = 1000 + 10 * 100 + (-5) * 200
    assert pair_portfolio.cash == expected_cash
    assert pair_portfolio.shares == (0, 0)

# pylint: disable=redefined-outer-name
def test_open_position(master_portfolio):
    """
    Test the open_position function.
    """
    # Setup
    pair_portfolio = portfolio.PairPortfolio(('StockA', 'StockB'), MockStrategy, master_portfolio)
    pair_portfolio.position_limit = 1000
    pair_portfolio.stock_pair_prices = (100, 200)  # example prices

    # Test "long A short B"
    trading.open_position(pair_portfolio, "long A short B")
    expected_shares = (1000 / 100, -1000 / 200)
    assert pair_portfolio.shares == expected_shares

    # Test "long B short A"
    trading.open_position(pair_portfolio, "long B short A")
    expected_shares = (-1000 / 100, 1000 / 200)
    assert pair_portfolio.shares == expected_shares

    # Test "no position"
    trading.open_position(pair_portfolio, "no position")
    assert pair_portfolio.shares == (0, 0)
