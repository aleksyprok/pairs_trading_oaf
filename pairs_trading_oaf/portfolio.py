"""
This module contains the portfolio classes.
"""
from typing import Tuple, Type
import numpy as np
from pairs_trading_oaf import strategies

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
    def __init__(self, position_limit: int, training_data_str: str, testing_data_str: str,
                 trading_fee: float = 0.0):
        self.position_limit = position_limit
        self.training_data_str = training_data_str
        self.testing_data_str = testing_data_str
        self.trading_fee = trading_fee
        self.pair_portfolios = []
        self.average_pertofolio_value_over_time = None
        self.strategy_strings = None
        self.average_values_over_time = None

    def add_pair_portfolio(self, pair_portfolio):
        """
        Add a pair portfolio to the master portfolio.
        """
        if not isinstance(pair_portfolio, PairPortfolio):
            raise TypeError("pair_portfolio must be an instance of PairPortfolio")
        self.pair_portfolios.append(pair_portfolio)

    def calc_strategy_strings(self):
        """
        Calculate a list of unique strategies used by the pair portfolios.
        """
        self.strategy_strings = []
        for pair_portfolio in self.pair_portfolios:
            if pair_portfolio.strategy.__class__.__name__ not in self.strategy_strings:
                self.strategy_strings.append(pair_portfolio.strategy.__class__.__name__)

    def calc_pairs_portfolio_index_dict(self):
        """
        Calculate a dictionary of indices for each pair portfolio.

        Need to have set self.strategy_strings first.

        The dictionary is of the form:
        pairs_portfolio_index_dict[strategy_string][stock_pair] = index
        """
        pairs_portfolio_index_dict = {}
        for strategy_string in self.strategy_strings:
            pairs_portfolio_index_dict[strategy_string] = {}
        for i, pair_portfolio in enumerate(self.pair_portfolios):
            strategy_string = pair_portfolio.strategy.__class__.__name__
            stock_a_label = pair_portfolio.stock_pair_labels[0]
            stock_a_label = stock_a_label[stock_a_label.find(':')+1:stock_a_label.find(')')]
            stock_b_label = pair_portfolio.stock_pair_labels[1]
            stock_b_label = stock_b_label[stock_b_label.find(':')+1:stock_b_label.find(')')]
            stock_pair_label = stock_a_label + '_' + stock_b_label
            pairs_portfolio_index_dict[strategy_string][stock_pair_label] = i
        return pairs_portfolio_index_dict

    def calc_average_values_over_time_by_strategy(self):
        """
        Calculate the average value of the portfolio over time
        across all the pair portfolios and across each strategy.

        Inputs:
        - Requires self.strategies to be calculated first.
        - Assumes that all pair portfolios have the same number of data points for their
          over_time lists.
        """
        value_strings = ["portfolio_value", "cash"]
        num_pairs_portfolio_counter = {}
        for strategy_string in self.strategy_strings:
            num_pairs_portfolio_counter[strategy_string] = 0
        self.average_values_over_time = {}
        for value_string in value_strings:
            self.average_values_over_time[value_string] = {}
            for strategy_string in self.strategy_strings:
                self.average_values_over_time[value_string][strategy_string] = \
                    np.zeros(len(self.pair_portfolios[0].__dict__[value_string + "_over_time"]))
        for pair_portfolio in self.pair_portfolios:
            strategy_string = pair_portfolio.strategy.__class__.__name__
            num_pairs_portfolio_counter[strategy_string] += 1
            for value_string in value_strings:
                self.average_values_over_time[value_string][strategy_string] += \
                    np.array(pair_portfolio.__dict__[value_string + "_over_time"])
        for value_string in value_strings:
            for strategy_string in self.strategy_strings:
                self.average_values_over_time[value_string][strategy_string] /= \
                    num_pairs_portfolio_counter[strategy_string]

    def average_portfolio_value_over_time(self):
        """
        Calculate the average value of the portfolio over time
        across all the pair portfolios.

        This function is not used anywhere so it is deprecated.
        """

        total_portfolio_value_over_time = \
            np.zeros(len(self.pair_portfolios[0].portfolio_value_over_time))
        for pair_portfolio in self.pair_portfolios:
            total_portfolio_value_over_time += np.array(pair_portfolio.portfolio_value_over_time)
        return total_portfolio_value_over_time / len(self.pair_portfolios)

    def average_cash_over_time(self):
        """
        Calculate the average cash over time
        across all the pair portfolios.

        This function is not used anywhere so it is deprecated.
        """
        total_cash_over_time = \
            np.zeros(len(self.pair_portfolios[0].cash_over_time))
        for pair_portfolio in self.pair_portfolios:
            total_cash_over_time += np.array(pair_portfolio.cash_over_time)
        return total_cash_over_time / len(self.pair_portfolios)

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
                 master_portfolio: MasterPortfolio,
                 cash: float = 1e6):
        super().__init__(master_portfolio.position_limit,
                         master_portfolio.training_data_str,
                         master_portfolio.testing_data_str)
        self.stock_pair_labels = stock_pair_labels
        self.strategy = strategy_class(self)
        self.cash = cash
        self.stock_pair_prices = (None, None) # Stores the latest prices of the stock pair
        self.portfolio_value = self.cash
        self.date = None # Stores the latest date
        self.position = "no position"
        self.shares = (0, 0) # Stores the number of shares of stock A and stock B
        self.cash_over_time = []
        self.dates_over_time = []
        self.position_over_time = []
        self.shares_over_time = []
        self.stock_pair_prices_over_time = []
        self.portfolio_value_over_time = []
        self.ratio_over_time = []

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
        self.cash_over_time.append(self.cash)
        self.dates_over_time.append(self.date)
        self.position_over_time.append(self.position)
        self.shares_over_time.append(self.shares)
        self.stock_pair_prices_over_time.append(self.stock_pair_prices)
        self.portfolio_value = self.cash
        if self.stock_pair_prices[0] is not None:
            self.portfolio_value += self.shares[0] * self.stock_pair_prices[0]
        if self.stock_pair_prices[1] is not None:
            self.portfolio_value += self.shares[1] * self.stock_pair_prices[1]
        self.portfolio_value_over_time.append(self.portfolio_value)
        if self.stock_pair_prices[0] is not None and self.stock_pair_prices[1] is not None:
            self.ratio_over_time.append(self.stock_pair_prices[0] / self.stock_pair_prices[1])
