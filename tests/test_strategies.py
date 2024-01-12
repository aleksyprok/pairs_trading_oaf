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

@patch('pairs_trading_oaf.strategies.StrategyB2.calc_initial_macd_signal')
def test_strategy_b2_initialization_no_initital_macd(mock_calc_initial_macd_signal):
    """
    This test checks that the StrategyB2 class is initialized correctly but without calling the
    calc_initial_macd_signal function.
    """

    # Arrange

    # Create a mock pair portfolio object
    mock_pair_portfolio = Mock()
    mock_pair_portfolio.stock_pair_labels = ('StockA', 'StockB')

    # Act
    strategy = strategies.StrategyB2(mock_pair_portfolio)

    # Assert
    assert strategy.pair_portfolio == mock_pair_portfolio
    assert strategy.macd.fast_period == 12
    assert strategy.macd.slow_period == 26
    assert strategy.macd.signal_period == 9
    assert strategy.macd.fast_ewma is None
    assert strategy.macd.slow_ewma is None
    assert strategy.macd.macd is None
    assert strategy.macd.signal is None
    mock_calc_initial_macd_signal.assert_called_once()

@patch('pairs_trading_oaf.data.read_csv')
def test_strategy_b2_initialization(mock_read_csv):
    """
    This test checks that the StrategyB2 class is initialized correctly and also tests the
    calc_initial_macd_signal function.
    """

    # Arrange

    # Create a mock pair portfolio object
    mock_pair_portfolio = Mock()
    mock_pair_portfolio.stock_pair_labels = ('StockA', 'StockB')

    # Create mock data for the initial window
    mock_data = pd.DataFrame({'Date': pd.date_range(start='2021-01-01', periods=3, freq='D'),
                              'StockA': np.array([1, 2, 3]),
                              'StockB': np.array([1, 1, 1]),
                            })
    mock_data.index = mock_data['Date']
    mock_read_csv.return_value = mock_data

    # Act
    strategy = strategies.StrategyB2(mock_pair_portfolio,
                                     fast_period=3,
                                     slow_period=4,
                                     signal_period=2,
                                     training_period=2)
    # alpha_fast = 1/2
    # alpha_slow = 2/5
    # alpha_signal = 2/3
    # ratios = [2, 3]
    # 1st iteration:
    # fast_ema = 2
    # slow_ema = 2
    # macd = 0
    # signal = 0
    # 2nd iteration:
    # fast_ema = alpha_fast * 3 + (1 - alpha_fast) * 2 = 5/2
    # slow_ema = alpha_slow * 3 + (1 - alpha_slow) * 2 = 12/5
    # macd = fast_ema - slow_ema = 1/10
    # signal = alpha_signal * (1/10) + (1 - alpha_signal) * 0 = 1/15

    # Assert
    assert strategy.pair_portfolio == mock_pair_portfolio
    assert strategy.macd.fast_period == 3
    assert strategy.macd.slow_period == 4
    assert strategy.macd.signal_period == 2
    assert strategy.macd.fast_ewma is not None
    assert strategy.macd.slow_ewma is not None
    assert strategy.macd.macd is not None
    assert strategy.macd.signal is not None
    assert np.isclose(strategy.macd.fast_ewma, 5/2)
    assert np.isclose(strategy.macd.slow_ewma, 12/5)
    assert np.isclose(strategy.macd.macd, 1/10)
    assert np.isclose(strategy.macd.signal, 1/15)

@patch('pairs_trading_oaf.data.read_csv')
def test_strategy_b2_calculate_new_position(mock_read_csv):
    """
    This test checks that the StrategyB2 class calculates the new position correctly.
    """
    # Arrange
    mock_pair_portfolio = Mock()
    mock_pair_portfolio.stock_pair_labels = ('StockA', 'StockB')
    mock_pair_portfolio.position = "no position"

    # Create mock training data for the initial window
    mock_data = pd.DataFrame({'Date': pd.date_range(start='2021-01-01', periods=3, freq='D'),
                              'StockA': np.array([1, 2, 3]),
                              'StockB': np.array([1, 1, 1]),
                            })
    mock_data.index = mock_data['Date']
    mock_read_csv.return_value = mock_data

    # Act
    strategy = strategies.StrategyB2(mock_pair_portfolio,
                                     fast_period=3,
                                     slow_period=4,
                                     signal_period=2,
                                     training_period=2)
    
    assert np.isclose(strategy.macd.fast_ewma, 5/2)
    assert np.isclose(strategy.macd.slow_ewma, 12/5)
    assert np.isclose(strategy.macd.macd, 1/10)
    assert np.isclose(strategy.macd.signal, 1/15)


    # Test 1: Check if the macd continues above the signal
    #         then the position shouldn't change.
    mock_pair_portfolio.stock_pair_prices = (3, 1)
    new_position = strategy.calculate_new_position()
    # fast_ewma = alpha_fast * 3 + (1 - alpha_fast) * 5/2 = 11/4
    # slow_ewma = alpha_slow * 3 + (1 - alpha_slow) * 12/5 = 66/25
    # macd = fast_ewma - slow_ewma = 11/100
    # signal = alpha_signal * (11/100) + (1 - alpha_signal) * 1/15 = 43/450
    assert np.isclose(strategy.macd.fast_ewma, 11/4)
    assert np.isclose(strategy.macd.slow_ewma, 66/25)
    assert np.isclose(strategy.macd.macd, 11/100)
    assert np.isclose(strategy.macd.signal, 43/450)
    assert new_position == 'no position'

    # Test 2: Check if the macd crosses below the signal
    #         then the position should change to long B short A.
    mock_pair_portfolio.stock_pair_prices = (1, 3)
    new_position = strategy.calculate_new_position()
    # fast_ewma = alpha_fast * (1/3) + (1 - alpha_fast) * 11/4 = 37/24
    # slow_ewma = alpha_slow * (1/3) + (1 - alpha_slow) * 66/25 = 644/375
    # macd = fast_ewma - slow_ewma = -527/3000
    # signal = alpha_signal * (-527/3000) + (1 - alpha_signal) * 43/450 = -1151/13500
    assert np.isclose(strategy.macd.fast_ewma, 37/24)
    assert np.isclose(strategy.macd.slow_ewma, 644/375)
    assert np.isclose(strategy.macd.macd, -527/3000)
    assert np.isclose(strategy.macd.signal, -1151/13500)
    assert new_position == 'long B short A'

    # Test 3: Check if the macd crosses above the signal
    #         then the position should change to long A short B.
    mock_pair_portfolio.stock_pair_prices = (10, 1)
    new_position = strategy.calculate_new_position()    
    # fast_ewma = alpha_fast * (10) + (1 - alpha_fast) * 37/24 = 277/48
    # slow_ewma = alpha_slow * (10) + (1 - alpha_slow) * 644/375 = 3144/625
    # macd = fast_ewma - slow_ewma = 22213/30000
    # signal = alpha_signal * (22213/30000) + (1 - alpha_signal) * (-1151/13500)
    #        = 188407/405000
    assert np.isclose(strategy.macd.fast_ewma, 277/48)
    assert np.isclose(strategy.macd.slow_ewma, 3144/625)
    assert np.isclose(strategy.macd.macd, 22213/30000)
    assert np.isclose(strategy.macd.signal, 188407/405000)
    assert new_position == 'long A short B'
