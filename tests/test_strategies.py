"""
Tests for the strategies module.
"""

from unittest.mock import Mock, patch
import numpy as np
import pandas as pd
from pairs_trading_oaf import strategies

# To initialise a Strategy object, we need to pass in a pair portfolio object.
# That pair portfolio object needs to have the following attributes:
# - training_data_str: the path to the training data but we will use a mock object
#   so we don't need to specify this.
# - stock_pair_labels: the labels of the stock pair so we know which columns to read

@patch('pairs_trading_oaf.data.read_csv')
def test_strategy_a_initialization(mock_read_csv):
    """
    This test checks that the StrategyA class is initialized correctly.
    To initialise a Strategy object, we need to pass in a pair portfolio object.
    That pair portfolio object needs to have the following attributes:
    - training_data_str: the path to the training data but we will use a mock object
                         so we don't need to specify this.
    - stock_pair_labels: the labels of the stock pair so we know which columns to read
    """

    # Arrange

    # Create a mock pair portfolio object
    mock_pair_portfolio = Mock()
    mock_pair_portfolio.stock_pair_labels = ('StockA', 'StockB')

    mock_data = pd.DataFrame({'Date': pd.date_range(start='2021-01-01', periods=100, freq='D'),
                              'StockA': np.random.rand(100) * 100,
                              'StockB': np.random.rand(100) * 200,
                              'StockC': np.random.rand(100) * 300,
                              'StockD': np.random.rand(100) * 400
                            })
    mock_data.index = mock_data['Date']
    mock_read_csv.return_value = mock_data

    # Act
    strategy = strategies.StrategyA(mock_pair_portfolio,
                                    window_size=60,
                                    z_threshold=1.0)

    # Assert
    assert strategy.pair_portfolio == mock_pair_portfolio
    assert strategy.window_size == 60
    assert strategy.window_prices.equals(mock_data[['StockA', 'StockB']].tail(60))
    assert strategy.z_threshold == 1.0

@patch('pairs_trading_oaf.data.read_csv')
def test_strategy_a_calculate_new_position(mock_read_csv):
    """
    This test checks that the StrategyA class calculates the new position correctly.
    """

    # Arrange
    mock_pair_portfolio = Mock()
    mock_pair_portfolio.stock_pair_labels = ('StockA', 'StockB')

    # Create mock training data for the initial window
    mock_data = pd.DataFrame({'Date': pd.date_range(start='2021-01-01', periods=100, freq='D'),
                              'StockA': np.ones(100) * 100,
                              'StockB': np.ones(100) * 200,
                            })
    mock_data.index = mock_data['Date']
    mock_read_csv.return_value = mock_data

    # Create a mock StrategyA object
    strategy = strategies.StrategyA(mock_pair_portfolio,
                                    window_size=60,
                                    z_threshold=1.0)

    # Test 1: z-score is 0
    mock_pair_portfolio.stock_pair_prices = (100, 200)
    new_position = strategy.calculate_new_position()
    assert new_position == 'no position'

    # Test 2: z-score is below the lower threshold
    mock_pair_portfolio.stock_pair_prices = (1, 1000)
    new_position = strategy.calculate_new_position()
    assert new_position == 'long A short B'

    # Test 3: z-score is above the upper threshold
    mock_pair_portfolio.stock_pair_prices = (1000, 1)
    new_position = strategy.calculate_new_position()
    assert new_position == 'long B short A'

@patch('pairs_trading_oaf.data.read_csv')
def test_strategy_b_initialization(mock_read_csv):
    """
    This test checks that the StrategyB class is initialized correctly.
    """

    # Arrange

    # Create a mock pair portfolio object
    mock_pair_portfolio = Mock()
    mock_pair_portfolio.stock_pair_labels = ('StockA', 'StockB')

    # Create mock data for the initial window
    mock_data = pd.DataFrame({'Date': pd.date_range(start='2021-01-01', periods=100, freq='D'),
                              'StockA': np.random.rand(100) * 100,
                              'StockB': np.random.rand(100) * 200
                            })
    mock_data.index = mock_data['Date']
    mock_read_csv.return_value = mock_data

    # Act
    strategy = strategies.StrategyB(mock_pair_portfolio)

    # Assert
    assert strategy.pair_portfolio == mock_pair_portfolio
    assert strategy.fast_window_size == 12
    assert strategy.slow_window_size == 26
    assert strategy.signal_window_size == 9
    max_window_size = np.max([strategy.fast_window_size, strategy.slow_window_size, strategy.signal_window_size])
    assert strategy.window_prices.equals(mock_data[['StockA', 'StockB']].tail(max_window_size))

def test_calc_macd_signal():
    # Arrange
    # Create a series of stock prices (ratios)
    stock_a_prices = np.linspace(100, 200, 100)
    stock_b_prices = np.linspace(200, 300, 100)
    ratio = pd.Series(stock_a_prices / stock_b_prices)

    # Define the window sizes directly in the test
    fast_window_size = 12
    slow_window_size = 26
    signal_window_size = 9

    # Act
    macd, signal = strategies.StrategyB.calc_macd_signal(ratio, slow_window_size, fast_window_size, signal_window_size) #asdadasdasdhfhfghfgasdasdassssssssss

    # Assert
    assert macd is not None
    assert signal is not None
    assert len(macd) == len(ratio)
    assert len(signal) == len(ratio)