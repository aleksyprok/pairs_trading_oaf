"""
This file contains code for each trading strategy. Try to keep the code that is specific
to each strategy in this module and code that is common to all strategies in the other modules.

When adding a new strategy, e.g. StrategyX make sure to use class StrategyX(BaseStrategy):
to ensure you are inheriting from the abstract base class.
"""

from abc import ABC, abstractmethod
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

class StrategyA(BaseStrategy):
    """
    Strategy A: Buy stock A and short stock B if the z-score of their ratios 
    is below the lower threshold.
    Buy stock B and short stock A if the z-score is above the upper threshold.
    Calculate the z-score using a moving average and standard deviation.
    """

    def __init__(self, pair_portfolio,
                 window_size: int = 60):
        self.pair_portfolio = pair_portfolio
        self.window_size = window_size
        self.z_threshold = 1
        self.window_prices = self.calculate_initial_window()

    def calculate_initial_window(self):
        """
        Calculate the initial window for the pair portfolio using the training data.

        Inputs:
        - master_portfolio: the master portfolio
        - stock_pair_labels: the labels of the stock pair

        Outputs:
        - window_data: a pandas DataFrame containing the stock A and stock B prices as columns
        and the dates as the index.
        """
        df_train = data.read_csv(self.pair_portfolio.training_data_str)
        df_train = df_train.tail(self.window_size)
        window_prices = df_train[list(self.pair_portfolio.stock_pair_labels)]

        return window_prices

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
            return "no position"
