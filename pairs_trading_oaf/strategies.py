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
    is below the lower threshold. This is a mean reversion strategy.
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
        std = max([ratio.std(), 1e-8])
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

    class MACDVals:
        """
        Class to store the MACD and signal values as well as the exponential weighted moving
        averages of the ratio of the stock prices.
        """
        def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
            self.fast_period = fast_period
            self.slow_period = slow_period
            self.signal_period = signal_period
            self.fast_ewma = None
            self.slow_ewma = None
            self.macd = None
            self.signal = None

    class OverTimeVals:
        """
        Class to store the MACD and signal values over time.
        """
        def __init__(self):
            self.macd = []
            self.signal = []
            self.fast_ewma = []
            self.slow_ewma = []

    def __init__(self, pair_portfolio,
                 fast_period: int = 12,
                 slow_period: int = 26,
                 signal_period: int = 9,
                 training_period: int = 100):
        self.pair_portfolio = pair_portfolio
        self.macd = self.MACDVals(fast_period, slow_period, signal_period)
        self.over_time_vals = self.OverTimeVals()
        self.calc_initial_macd_signal(training_period)

    def calc_macd_signal(self, ratio):
        """
        Update the MACD and signal values using the latest ratio.

        Returns:
        - macd: the latest MACD value
        - signal: the latest signal value
        Overwrites the stored values of the fast and slow exponential moving averages
        of the price ratios.
        """
        alpha_fast = 2 / (self.macd.fast_period + 1)
        alpha_slow = 2 / (self.macd.slow_period + 1)
        alpha_signal = 2 / (self.macd.signal_period + 1)
        self.macd.fast_ewma = alpha_fast * ratio + (1 - alpha_fast) * self.macd.fast_ewma
        self.macd.slow_ewma = alpha_slow * ratio + (1 - alpha_slow) * self.macd.slow_ewma
        macd = self.macd.fast_ewma - self.macd.slow_ewma
        signal = alpha_signal * macd + (1 - alpha_signal) * self.macd.signal
        return macd, signal

    def calc_initial_macd_signal(self, training_period):
        """
        Calculate the initial MACD and signal values using the training data.
        """
        df_train = data.read_csv(self.pair_portfolio.training_data_str)
        df_train = df_train.tail(training_period)
        ratios = df_train[self.pair_portfolio.stock_pair_labels[0]] \
               / df_train[self.pair_portfolio.stock_pair_labels[1]]
        for i, ratio in enumerate(ratios):
            if i == 0:
                self.macd.fast_ewma = ratio
                self.macd.slow_ewma = ratio
                self.macd.macd = 0
                self.macd.signal = 0
            else:
                new_macd, new_signal = self.calc_macd_signal(ratio)
                self.macd.macd = new_macd
                self.macd.signal = new_signal

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
        ratio = new_prices[0] / new_prices[1]
        new_macd, new_signal = self.calc_macd_signal(ratio)
        old_macd = self.macd.macd
        old_signal = self.macd.signal

        if new_macd > new_signal and old_macd < old_signal:
            # MACD crossed above signal line so long stock A and short stock B
            position = 'long A short B'
        elif new_macd < new_signal and old_macd > old_signal:
            # MACD crossed below signal line so long stock B and short stock A
            position = 'long B short A'
        else:
            # Don't change the position if the MACD and signal line do not cross
            position = self.pair_portfolio.position

        # Update the stored MACD and signal values ready for the next day
        self.macd.macd = new_macd
        self.macd.signal = new_signal

        self.over_time_vals.fast_ewma.append(self.macd.fast_ewma)
        self.over_time_vals.slow_ewma.append(self.macd.slow_ewma)
        self.over_time_vals.macd.append(self.macd.macd)
        self.over_time_vals.signal.append(self.macd.signal)

        return position

class StrategyC(BaseStrategy):
    """
    This is a mean reversion strategy that uses Bollinger Bands to determine the position.

    To be honest, this is very similar to StrategyA but uses Bollinger Bands instead of
    z-scores to determine the position.
    """

    def __init__(self, pair_portfolio,
                 window_size: int = 45,
                 num_std: int = 2):
        self.pair_portfolio = pair_portfolio
        self.window_size = window_size
        self.num_std = num_std
        self.window_prices = self.calculate_initial_window(self.window_size)
        self.upper_band_over_time = []
        self.lower_band_over_time = []

    def calculate_new_position(self):
        """
        Calculate the new position for the pair portfolio.

        Takes the latest prices of the stock pair and calculates the new position based on the
        Bollinger Bands. The new position can be one of the following strings:
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
        std = max([ratio.std(), 1e-8])
        upper_band = mean + self.num_std * std
        lower_band = mean - self.num_std * std
        self.upper_band_over_time.append(upper_band)
        self.lower_band_over_time.append(lower_band)
        if ratio.iloc[-1] > upper_band:
            return 'long B short A'
        elif ratio.iloc[-1] < lower_band:
            return 'long A short B'
        else:
            return self.pair_portfolio.position

class StrategyD(BaseStrategy):
    """
    This strategy is meant to be as close to Golden's as possible.
    |z| ≤ 1: Close (profit)
    1.5 < |z| ≤ 2: Open position
    |z| > 2: Close (stop loss) Bollinger Bands: mean ± x SD of 45-day ratio
    Factor x set by risk, volatility
    If ratio > upper band, short the ratio.
    """
    def __init__(self, pair_portfolio,
                 tight_window_size: int = 5,
                 wider_window_size: int = 60,
                 open_threshold: float = 1.5,
                 stop_threshold: float = 2.0,
                 close_threshold: float = 1):
        self.pair_portfolio = pair_portfolio
        self.tight_window_size = tight_window_size
        self.wider_window_size = wider_window_size
        self.open_threshold = open_threshold
        self.stop_threshold = stop_threshold
        self.close_threshold = close_threshold
        self.tight_window_prices = self.calculate_initial_window(self.tight_window_size)
        self.wider_window_prices = self.calculate_initial_window(self.wider_window_size)

    def calculate_new_position(self):
        """
        Calculate the new position for the pair portfolio.

        If |z| ≤ 1: Close (profit)
        1.5 < |z| ≤ 2: Open position
        |z| > 2: Close (stop loss)
        """
        new_prices = self.pair_portfolio.stock_pair_prices
        current_date = self.pair_portfolio.date
        stock_pair_labels = self.pair_portfolio.stock_pair_labels
        new_data = pd.DataFrame([new_prices],
                                columns=stock_pair_labels,
                                index=[current_date])
        self.tight_window_prices = pd.concat([self.tight_window_prices, new_data])
        self.tight_window_prices = self.tight_window_prices.iloc[1:]
        self.wider_window_prices = pd.concat([self.wider_window_prices, new_data])
        self.wider_window_prices = self.wider_window_prices.iloc[1:]
        tight_ratio = self.tight_window_prices[stock_pair_labels[0]] \
                    / self.tight_window_prices[stock_pair_labels[1]]
        wider_ratio = self.wider_window_prices[stock_pair_labels[0]] \
                    / self.wider_window_prices[stock_pair_labels[1]]
        tight_ratio_mean = tight_ratio.mean()
        wider_ratio_mean = wider_ratio.mean()
        wider_ratio_std = wider_ratio.std()
        z_score = (tight_ratio_mean - wider_ratio_mean) / wider_ratio_std

        if np.abs(z_score) <= self.close_threshold:
            # |z| ≤ 1 (Close position, profit)
            return 'no position'
        elif np.abs(z_score) > self.stop_threshold:
            # |z| > 2 (Close position, stop loss)
            return 'no position'
        elif np.abs(z_score) <= self.open_threshold:
            #1 < |z| ≤ 1.5 (Don't change position)
            return self.pair_portfolio.position
        else:
            # 1.5 < |z| ≤ 2 (Open position)
            if z_score > 0:
                return 'long B short A'
            else:
                return 'long A short B'

