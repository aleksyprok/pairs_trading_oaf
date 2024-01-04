"""
This module contains the portfolio classes.
"""
from typing import Tuple, Type
import pairs_trading_oaf.strategies as strategies

class MasterPortfolio:
    """
    Class to represent the master portfolio. This is the top-level portfolio and contains
    all the pair portfolios which in turn contain the individual stock portfolios.
    Different pair portfolios can have different strategies.

    Note that the training data is used by some training strategies to calculate the
    trading thresholds. For example, the training data is used for a moving average
    strategy to calculate the moving average until the time of the lower bound of the
    window is greater than the trading start date. The testing data is used to execute
    trades.
    """
    def __init__(self, position_limit: int, training_data_str: str, testing_data_str: str):
        self.position_limit = position_limit
        self.training_data_str = training_data_str
        self.testing_data_str = testing_data_str
        self.total_pnl = 0
        self.total_pnl_over_time = []
        self.pair_portfolios = []

    def add_pair_portfolio(self, pair_portfolio):
        """
        Add a pair portfolio to the master portfolio.
        """
        if not isinstance(pair_portfolio, PairPortfolio):
            raise TypeError("pair_portfolio must be an instance of PairPortfolio")
        self.pair_portfolios.append(pair_portfolio)

class PairPortfolio(MasterPortfolio):
    """
    Class to represent a pair portfolio. This portfolio contains a single pairs of stocks
    and a strategy.

    The PairPortfolio class inherits from the MasterPortfolio class although we may make it
    an independent class in the future.

    Note that we will refer to stock_pair_labels[0] as stock A and stock_pair_labels[1] as
    stock B.

    The possible values of self.position are:
    - "no position"
    - "long A short B"
    - "long B short A"
    """
    def __init__(self,
                 stock_pair_labels: Tuple[str, str],
                 strategy_class: Type[strategies.BaseStrategy],
                 master_portfolio: MasterPortfolio):
        super().__init__(master_portfolio.position_limit,
                         master_portfolio.training_data_str,
                         master_portfolio.testing_data_str)
        self.stock_pair_labels = stock_pair_labels
        self.strategy = strategy_class(self)
        self.cash = 0
        self.stock_pair_prices = (None, None) # Stores the latest prices of the stock pair
        self.date = None # Stores the latest date
        self.position = "no position"
        self.shares = (0, 0) # Stores the number of shares of stock A and stock B
        # If you don't wish to store a value over time, set the corresponding list to None
        self.cash_over_time = []

    def update_prices_and_date(self, date, row):
        """
        Update the pair portfolio with the latest prices and date from a new row of data
        from a csv file.
        """
        self.stock_pair_prices = (row[self.stock_pair_labels[0]],
                                  row[self.stock_pair_labels[1]])
        self.date = date

    def update_over_time_values(self):
        """
        Update the portfolio over time.
        """
        if self.cash_over_time is not None:
            self.cash_over_time.append(self.cash)
