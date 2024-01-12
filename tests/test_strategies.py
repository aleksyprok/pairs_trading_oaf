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
    mock_pair_portfolio.position = "no position"

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
    mock_pair_portfolio.position = "no position"

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
    max_window_size = np.max([strategy.fast_window_size,
                              strategy.slow_window_size,
                              strategy.signal_window_size])
    assert strategy.window_prices.equals(mock_data[['StockA', 'StockB']].tail(max_window_size+50))

def test_calc_macd_signal():
    """
    This test checks that the calc_macd_signal function returns the correct output.
    """

    # Arrange
    # Create a series of stock prices (ratios)
    stock_a_prices = np.array([4, 3, 1, 2, 5, 1])
    stock_b_prices = np.array([1, 1, 1, 1, 1, 1])
    ratio = pd.Series(stock_a_prices / stock_b_prices)

    # Define the window sizes directly in the test
    fast_window_size = 2
    slow_window_size = 4
    signal_window_size = 2

    # alpha = 2 / (window_size + 1)
    # alpha_fast = 2 / = 2/3
    # fast_ema[0] = ratio[0] = 4
    # fast_ema[1] = (1 - alpha) * 4 + alpha * 3 =  10/3  = 3.3333333
    # fast_ema[2] = (1 - alpha) * 10/3 + alpha * 1 = 16/9 = 1.7777777
    # fast_ema[3] = (1 - alpha) * 16/9 + alpha * 2 = 52/27 = 1.9259259
    # fast_ema[4] = (1 - alpha) * 52/27 + alpha * 5 = 322/81 = 3.9753086
    # fast_ema[5] = (1 - alpha) * 322/81 + alpha * 1 = 484/243 = 1.9917695
    # fast_ema = [4, 10/3, 16/9, 52/27, 322/81, 484/243]
    # alpha_slow = 2 / 5
    # slow_ema[0] = 4
    # slow_ema[0] = (1 - alpha) * 4 + alpha * 3 = 18/5 = 3.6
    # slow_ema[1] = (1 - alpha) * 18/5 + alpha * 1 = 64/25 = 2.56
    # slow_ema[2] = (1 - alpha) * 64/25 + alpha * 2 = 292/125 = 2.336
    # slow_ema[3] = (1 - alpha) * 292/125 + alpha * 5 = 2126/625 = 3.4016
    # slow_ema[4] = (1 - alpha) * 2126/625 + alpha * 1 = 7628/3125 = 2.44096
    # slow_ema = [4, 18/5, 64/25, 292/125, 2126/625, 7628/3125]
    # macd = fast_ema - slow_ema
    # macd = [0, -4/15, -176/225, -1384/3375, 29044/50625,-341104/759375]
    #      = [0, -0.2666666, -0.7822222, -0.4103703, 0.5733333, -0.4491852]
    # alpha_signal = 2 / 3
    # signal[0] = macd[0] = 0
    # signal[1] = (1 - alpha) * 0 + alpha * (-4/15) = -8/45 = -0.1777777
    # signal[2] = (1 - alpha) * (-8/45) + alpha * (-176/225) = -392/675 = -0.5807407
    # signal[3] = (1 - alpha) * (-392/675) + alpha * (-1384/3375) = -1576/3375 = -0.4669629
    # signal[4] = (1 - alpha) * (-1576/3375) + alpha * (29044/50625) = 34448/151875 = 0.22681811
    # signal[5] = (1 - alpha) * (34448/151875) + alpha * (-341104/759375) = -509968/2278125
    #           = -0.2238543
    # signal = np.array([0, -8/45, -392/675, -1576/3375, 34448/151875, -509968/2278125])

    # Act
    macd, signal = strategies.StrategyB.calc_macd_signal(ratio,
                                                         slow_window_size,
                                                         fast_window_size,
                                                         signal_window_size)

    # Assert
    assert macd is not None
    assert signal is not None
    assert len(macd) == len(ratio)
    assert len(signal) == len(ratio)
    # assert macd = [0, -4/15, -176/225, -1384/3375, 29044/50625,-341104/759375]
    assert np.allclose(macd, [0, -4/15, -176/225, -1384/3375, 29044/50625,-341104/759375])
    assert np.allclose(signal, [0, -8/45, -392/675, -1576/3375, 34448/151875, -509968/2278125])
