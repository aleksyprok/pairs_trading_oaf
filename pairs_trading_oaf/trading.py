"""
Functions to execute pairs trading strategy.
"""

import yfinance as yf

class Portfolio:
    """
    Class to represent a portfolio.
    """

    def __init__(self):
        """
        Initialize the portfolio.
        """
        self.cash = 0
        self.stock_a = 0
        self.stock_b = 0

    def get_value(self, stock_a_price, stock_b_price):
        """
        Get the value of the portfolio.
        """
        return self.cash + self.stock_a * stock_a_price + self.stock_b * stock_b_price

def run_pairs_trade_strategy(stock_a_ticker: str = 'AAPL',
                             stock_b_ticker: str = 'MSFT',
                             training_start_date: str = '2019-01-01',
                             training_end_date: str = '2021-01-01',
                             testing_start_date: str = '2021-01-02',
                             testing_end_date: str = '2022-01-01'):
    """
    Run the pairs trading strategy.
    """

    stock_a_training_prices = yf.download(stock_a_ticker,
                                          start=training_start_date,
                                          end=training_end_date)['Close']
    stock_b_training_prices = yf.download(stock_b_ticker,
                                          start=training_start_date,
                                          end=training_end_date)['Close']
    stock_a_testing_prices = yf.download(stock_a_ticker,
                                         start=testing_start_date,
                                         end=testing_end_date)['Close']
    stock_b_testing_prices = yf.download(stock_b_ticker,
                                         start=testing_start_date,
                                         end=testing_end_date)['Close']
    
    # Calculate ratio
    ratio = stock_a_training_prices / stock_b_training_prices

    # Calculate mean and standard deviation
    mean = ratio.mean()
    std = ratio.std()

    # Calculate thresholds
    sell_threshold = mean + 0.5 * std
    buy_threshold = mean - 0.5 * std
    
    return 1
