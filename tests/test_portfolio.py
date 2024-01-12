"""
Test the routines in the portfolio module.
"""
from unittest.mock import Mock
import numpy as np
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

# Use mock pair portfolio to test the calc_strategy_strings method
def test_calc_strategy_strings():
    """
    Test the calc_strategy_strings method of the MasterPortfolio class.
    """
    # Arrange
    master_portfolio = portfolio.MasterPortfolio(POSITION_LIMIT, TRAINING_DATA, TESTING_DATA)
    mock_pair_portfolio1 = Mock()
    mock_pair_portfolio1.strategy = Mock()
    mock_pair_portfolio1.strategy.__class__.__name__ = "MockStrategy1"
    mock_pair_portfolio2 = Mock()
    mock_pair_portfolio2.strategy = Mock()
    mock_pair_portfolio2.strategy.__class__.__name__ = "MockStrategy2"
    master_portfolio.pair_portfolios = [mock_pair_portfolio1, mock_pair_portfolio2]

    # Act
    master_portfolio.calc_strategy_strings()

    # Assert
    assert master_portfolio.strategy_strings == ["MockStrategy1", "MockStrategy2"]

def test_calc_pairs_portfolio_index_dict():
    """
    Test the calc_pairs_portfolio_index_dict method of the MasterPortfolio class.
    """

    # Arrange
    master_portfolio = portfolio.MasterPortfolio(POSITION_LIMIT, TRAINING_DATA, TESTING_DATA)
    mock_pair_portfolio1 = Mock()
    mock_pair_portfolio1.strategy = Mock()
    mock_pair_portfolio1.strategy.__class__.__name__ = "MockStrategy1"
    mock_pair_portfolio1.stock_pair_labels = (":StockA)", ":StockB)")
    mock_pair_portfolio2 = Mock()
    mock_pair_portfolio2.strategy = Mock()
    mock_pair_portfolio2.strategy.__class__.__name__ = "MockStrategy2"
    mock_pair_portfolio2.stock_pair_labels = (":StockC)", ":StockD)")
    master_portfolio.pair_portfolios = [mock_pair_portfolio2, mock_pair_portfolio1]

    # Act
    master_portfolio.calc_strategy_strings()
    pairs_portfolio_index_dict = master_portfolio.calc_pairs_portfolio_index_dict()

    # Assert
    pairs_portfolio_index_dict_test = {}
    pairs_portfolio_index_dict_test["MockStrategy2"] = {}
    pairs_portfolio_index_dict_test["MockStrategy2"]["StockC_StockD"] = 0
    pairs_portfolio_index_dict_test["MockStrategy1"] = {}
    pairs_portfolio_index_dict_test["MockStrategy1"]["StockA_StockB"] = 1
    assert pairs_portfolio_index_dict == pairs_portfolio_index_dict_test

def test_calc_average_values_over_time_by_strategy():
    """
    Test the calc_average_values_over_time_by_strategy method of the MasterPortfolio class.
    """
    
    # Arrange
    master_portfolio = portfolio.MasterPortfolio(POSITION_LIMIT, TRAINING_DATA, TESTING_DATA)
    mock_pair_portfolio1 = Mock()
    mock_pair_portfolio1.strategy = Mock()
    mock_pair_portfolio1.strategy.__class__.__name__ = "MockStrategy1"
    mock_pair_portfolio1.portfolio_value_over_time = [1, 2, 3, 4, 5]
    mock_pair_portfolio1.cash_over_time = [6, 7, 8, 9, 10]
    mock_pair_portfolio2 = Mock()
    mock_pair_portfolio2.strategy = Mock()
    mock_pair_portfolio2.strategy.__class__.__name__ = "MockStrategy1"
    mock_pair_portfolio2.portfolio_value_over_time = [11, 12, 13, 14, 15]
    mock_pair_portfolio2.cash_over_time = [16, 17, 18, 19, 20]
    master_portfolio.pair_portfolios = [mock_pair_portfolio1, mock_pair_portfolio2]

    # Act
    master_portfolio.calc_strategy_strings()
    master_portfolio.calc_average_values_over_time_by_strategy()

    # Assert
    assert np.array_equal(master_portfolio.average_values_over_time["portfolio_value"]["MockStrategy1"],
                          np.array([6, 7, 8, 9, 10]))
    # np.
    assert np.array_equal(master_portfolio.average_values_over_time["cash"]["MockStrategy1"],
                          np.array([11, 12, 13, 14, 15]))
    
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
