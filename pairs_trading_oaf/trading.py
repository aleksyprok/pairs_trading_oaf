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
    
    ratio = stock_a_training_prices / stock_b_training_prices

    mean = ratio.mean()
    std = ratio.std()

    long_stock_a_threshold = mean - 0.5 * std
    long_stock_b_threshold = mean + 0.5 * std

    # Execute strategy
    execute_trades(stock_a_ticker,
                   stock_b_ticker,
                   testing_start_date,
                   testing_end_date,
                   long_stock_a_threshold,
                   long_stock_b_threshold)
    
    return 1

def execute_trades(stock_a_ticker, stock_b_ticker, start_date, end_date,
                   long_stock_a_threshold, long_stock_b_threshold):

    stock_a_prices = yf.download(stock_a_ticker,
                                 start=start_date,
                                 end=end_date)['Close']
    stock_b_prices = yf.download(stock_b_ticker,
                                 start=start_date,
                                 end=end_date)['Close']
    ratio = stock_a_prices / stock_b_prices

    for it in range(len(ratio)):
        if ratio.iloc[it] < long_stock_a_threshold:
            print(f"Long {stock_a_ticker} and short {stock_b_ticker}")
        elif ratio.iloc[it] > long_stock_b_threshold:
            print(f"Short {stock_a_ticker} and long {stock_b_ticker}")
        else:
            print("No trade")
