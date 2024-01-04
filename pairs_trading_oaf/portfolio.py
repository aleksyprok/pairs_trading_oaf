"""
This module contains the portfolio classes.
"""
from typing import Callable

class MasterPortfolio:
    """
    Class to represent the master portfolio. This is the top-level portfolio and contains
    all the pair portfolios which in turn contain the individual stock portfolios.
    Different pair portfolios can have different strategies.
    """
    def __init__(self):
        self.cash = 0
        self.total_pnl = 0
        self.total_pnl_over_time = []

class PairPortfolio(MasterPortfolio):
    """
    Class to represent a pair portfolio. This portfolio contains a single pairs of stocks
    and a strategy.

    The PairPortfolio class inherits from the MasterPortfolio class although we may make it
    an independent class in the future.
    """
    def __init__(self, stock_a_column_label: str, stock_b_column_label: str, strategy: Callable):
        super().__init__()
        self.stock_a_column_label = stock_a_column_label
        self.stock_b_column_label = stock_b_column_label
        self.strategy = strategy
        self.pnl = 0
