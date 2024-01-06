"""
Test the routines in the portfolio module.
"""
import pandas as pd
from pairs_trading_oaf import portfolio
from pairs_trading_oaf import strategies

TRAINING_DATA = "path/to/training_data.csv"
TESTING_DATA = "path/to/testing_data.csv"
POSITION_LIMIT = 1
STOCK_PAIR_LABELS = ("StockA", "StockB")

class MockStrategy(strategies.BaseStrategy):
    """
    Mock strategy class of the same format as those in the strategies module
    for testing purposes.
    """
    def __init__(self, pair_portfolio):
        pass

    def calculate_new_position(self):
        pass

def test_master_portfolio_initialization():
    """
    Test the initialization of the MasterPortfolio class.
    """
    master_portfolio = portfolio.MasterPortfolio(POSITION_LIMIT, TRAINING_DATA, TESTING_DATA)
    assert master_portfolio.position_limit == POSITION_LIMIT
    assert master_portfolio.training_data_str == TRAINING_DATA
    assert master_portfolio.testing_data_str == TESTING_DATA
    assert isinstance(master_portfolio.pair_portfolios, list)

def test_add_pair_portfolio():
    """
    Test the add_pair_portfolio method of the MasterPortfolio class.
    """
    master_portfolio = portfolio.MasterPortfolio(POSITION_LIMIT, TRAINING_DATA, TESTING_DATA)
    pair_portfolio = portfolio.PairPortfolio(STOCK_PAIR_LABELS, MockStrategy, master_portfolio)
    master_portfolio.add_pair_portfolio(pair_portfolio)
    assert pair_portfolio in master_portfolio.pair_portfolios

def test_average_portfolio_value_over_time():
    """
    Test the average_portfolio_value_over_time method of the MasterPortfolio class.
    """
    # Arrange
    master_portfolio = portfolio.MasterPortfolio(POSITION_LIMIT, TRAINING_DATA, TESTING_DATA)

    # Create three identical pair portfolios
    for _ in range(3):
        pair_portfolio = portfolio.PairPortfolio(STOCK_PAIR_LABELS, MockStrategy, master_portfolio)
        master_portfolio.add_pair_portfolio(pair_portfolio)

        for date in pd.date_range(start='2021-01-01', periods=5, freq='D'):
            test_row = {STOCK_PAIR_LABELS[0]: 100, STOCK_PAIR_LABELS[1]: 200}
            pair_portfolio.update_prices_and_date(str(date), test_row)
            pair_portfolio.cash = 1000 + date.day
            pair_portfolio.update_over_time_values()

    # Calculate expected average portfolio value over time
    expected_average_value = [1001, 1002, 1003, 1004, 1005]

    # Act
    actual_average_value = master_portfolio.average_portfolio_value_over_time()

    # Assert
    for actual, expected in zip(actual_average_value, expected_average_value):
        assert actual == expected

def test_pair_portfolio_initialization():
    """
    Test the initialization of the PairPortfolio class.
    """
    master_portfolio = portfolio.MasterPortfolio(POSITION_LIMIT, TRAINING_DATA, TESTING_DATA)
    pair_portfolio = portfolio.PairPortfolio(STOCK_PAIR_LABELS, MockStrategy, master_portfolio)
    assert pair_portfolio.stock_pair_labels == STOCK_PAIR_LABELS
    assert isinstance(pair_portfolio.strategy, MockStrategy)

def test_update_prices_and_date():
    """
    Test the update_prices_and_date method of the PairPortfolio class.
    """
    master_portfolio = portfolio.MasterPortfolio(POSITION_LIMIT, TRAINING_DATA, TESTING_DATA)
    pair_portfolio = portfolio.PairPortfolio(STOCK_PAIR_LABELS, MockStrategy, master_portfolio)
    test_date = "2021-01-01"
    test_row = {STOCK_PAIR_LABELS[0]: 100.0, STOCK_PAIR_LABELS[1]: 200.0}
    pair_portfolio.update_prices_and_date(test_date, test_row)
    assert pair_portfolio.date == test_date
    assert pair_portfolio.stock_pair_prices == (100.0, 200.0)

def test_update_over_time_values():
    """
    Test the update_over_time_values method of the PairPortfolio class.
    """
    master_portfolio = portfolio.MasterPortfolio(POSITION_LIMIT, TRAINING_DATA, TESTING_DATA)
    pair_portfolio = portfolio.PairPortfolio(STOCK_PAIR_LABELS, MockStrategy, master_portfolio)
    pair_portfolio.cash = 500
    pair_portfolio.date = "2021-01-01"
    pair_portfolio.update_over_time_values()
    assert pair_portfolio.cash_over_time == [500]
    assert pair_portfolio.dates_over_time == ["2021-01-01"]
    pair_portfolio.cash = 800
    pair_portfolio.date = "2021-01-05"
    pair_portfolio.update_over_time_values()
    assert pair_portfolio.cash_over_time == [500, 800]
    assert pair_portfolio.dates_over_time == ["2021-01-01", "2021-01-05"]
