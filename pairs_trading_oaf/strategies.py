"""
This file contains code for each trading strategy. Try to keep the code that is specific
to each strategy in this module and code that is common to all strategies in the other modules.

When adding a new strategy, e.g. StrategyX make sure to use class StrategyX(BaseStrategy):
to ensure you are inheriting from the abstract base class.

The stategy class simply needs to calculate the position for the pair portfolio
given the latest prices of the stock pair. The position can be one of the following strings:
- "no position"
- "long A short B"
- "long B short A"

A new strategy should follow this format:
class StrategyX(BaseStrategy):
    def __init__(self, pair_portfolio, <other arguments>):
        self.pair_portfolio = pair_portfolio # Need to link the strategy to a pair portfolio
        <other initialisation code>

    def calculate_new_position(self):
        <code to calculate the new position>
        return new_position
"""

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from pairs_trading_oaf import data

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    """

    @abstractmethod
    def calculate_new_position(self):
        """
        Calculate the new position for the pair portfolio.
        This method needs to be implemented by all concrete strategy classes.

        Returns:
        - new_position: the new position for the pair portfolio. Which can be one of the following
        strings:
          - "no position"
          - "long A short B"
          - "long B short A"
        """

    def calculate_initial_window(self, window_size: int):
        """
        Calculate the initial window for the pair portfolio using the training data.

        Inputs:
        - master_portfolio: the master portfolio
        - stock_pair_labels: the labels of the stock pair

        Outputs:
        - window_data: a pandas DataFrame containing the stock A and stock B prices as columns
        and the dates as the index.
        """
        df_train = data.read_csv(self.pair_portfolio.training_data_str) # pylint: disable=no-member
        df_train = df_train.tail(window_size)
        window_prices = df_train[list(self.pair_portfolio.stock_pair_labels)] # pylint: disable=no-member

        return window_prices

class StrategyA(BaseStrategy):
    """
    Strategy A: Buy stock A and short stock B if the z-score of their ratios 
    is below the lower threshold.
    Buy stock B and short stock A if the z-score is above the upper threshold.
    Calculate the z-score using a moving average and standard deviation.
    """

    def __init__(self, pair_portfolio,
                 window_size: int = 60,
                 z_threshold: float = 1.0):
        self.pair_portfolio = pair_portfolio
        self.window_size = window_size
        self.z_threshold = z_threshold
        self.window_prices = self.calculate_initial_window(self.window_size)

    def calculate_new_position(self):
        """
        Calculate the new position for the pair portfolio.

        Takes the latest prices of the stock pair and calculates the new position based on the
        z-score of the ratio of the stock prices. The new position can be one of the following
        strings:
        - "no position"
        - "long A short B"
        - "long B short A"
        """
        new_prices = self.pair_portfolio.stock_pair_prices
        current_date = self.pair_portfolio.date
        stock_pair_labels = self.pair_portfolio.stock_pair_labels
        new_data = pd.DataFrame([new_prices],
                                columns=stock_pair_labels,
                                index=[current_date])
        self.window_prices = pd.concat([self.window_prices, new_data])
        self.window_prices = self.window_prices.iloc[1:]
        ratio = self.window_prices[stock_pair_labels[0]] / self.window_prices[stock_pair_labels[1]]
        mean = ratio.mean()
        std = ratio.std()
        z_score = (ratio.iloc[-1] - mean) / std

        if z_score < -self.z_threshold:
            return 'long A short B'
        elif z_score > self.z_threshold:
            return 'long B short A'
        else:
            return self.pair_portfolio.position

class StrategyB(BaseStrategy):
    """
    Moving Average Convergence Divergence (MACD) strategy.

    The MACD strategy is a trend following strategy that uses the difference between
    two moving averages of the stock prices to determine the position.

    The MACD line is the difference between the 26-day and 12-day exponential moving averages
    of the stock prices. The signal line is the 9-day exponential moving average of the MACD line.

    The position is long stock A and short stock B if the MACD crosses above the signal line.

    The position is long stock B and short stock A if the MACD crosses below the signal line.
    """

    def __init__(self, pair_portfolio,
                 fast_window_size: int = 12,
                 slow_window_size: int = 26,
                 signal_window_size: int = 9):
        self.pair_portfolio = pair_portfolio
        self.fast_window_size = fast_window_size
        self.slow_window_size = slow_window_size
        self.signal_window_size = signal_window_size
        max_window_size = np.max([self.fast_window_size,
                                  self.slow_window_size,
                                  self.signal_window_size])
        # Set the window size to be the maximum window size plus 50
        # This is to ensure that we have enough data to calculate the MACD and signal line
        window_size = max_window_size + 50
        self.window_prices = self.calculate_initial_window(window_size)

    @staticmethod
    def calc_macd_signal(ratio, slow_window_size, fast_window_size, signal_window_size):
        """
        Calculate the MACD and signal line for a given stock pair ratio.
        """
        fast_ema = ratio.ewm(span=fast_window_size, adjust=False).mean()
        slow_ema = ratio.ewm(span=slow_window_size, adjust=False).mean()
        macd = fast_ema - slow_ema
        signal = macd.ewm(span=signal_window_size, adjust=False).mean()
        return macd, signal

    def calculate_new_position(self):
        """
        Calculate the new position for the pair portfolio.

        Takes the latest prices of the stock pair and calculates the new position based on the
        MACD and signal line. The new position can be one of the following strings:
        - "no position"
        - "long A short B"
        - "long B short A"
        """
        new_prices = self.pair_portfolio.stock_pair_prices
        current_date = self.pair_portfolio.date
        stock_pair_labels = self.pair_portfolio.stock_pair_labels
        new_data = pd.DataFrame([new_prices],
                                columns=stock_pair_labels,
                                index=[current_date])
        self.window_prices = pd.concat([self.window_prices, new_data])
        self.window_prices = self.window_prices.iloc[1:]
        ratio = self.window_prices[stock_pair_labels[0]] / self.window_prices[stock_pair_labels[1]]
        macd, signal = self.calc_macd_signal(ratio,
                                             self.slow_window_size,
                                             self.fast_window_size,
                                             self.signal_window_size)
        if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] < signal.iloc[-2]:
            # MACD crossed above signal line so long stock A and short stock B
            return 'long A short B'
        elif macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] > signal.iloc[-2]:
            # MACD crossed below signal line so long stock B and short stock A
            return 'long B short A'
        else:
            # Don't change the position if the MACD and signal line do not cross
            return self.pair_portfolio.position