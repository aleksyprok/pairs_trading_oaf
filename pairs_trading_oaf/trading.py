"""
Functions to execute pairs trading strategy.
"""
import os
import pandas as pd
import yfinance as yf

class Portfolio:
    """
    Class to represent a portfolio.
    """

    def __init__(self, stock_a_ticker: str, stock_b_ticker: str):
        """
        Initialize the portfolio.
        """
        self.cash = 0
        self.stock_a = 0
        self.stock_b = 0
        self.position = None
        self.position_limit = 1000000 # USD
        self.stock_a_ticker = stock_a_ticker
        self.stock_b_ticker = stock_b_ticker
        self.long_stock_a_threshold = None
        self.long_stock_b_threshold = None
        self.cash_over_time = []
        self.stock_a_over_time = []
        self.stock_b_over_time = []
        self.position_over_time = []
        self.trading_start_date = None
        self.trading_end_date = None

    def calculate_trading_thresholds(self, training_start_date: str, training_end_date: str):
        """
        Calculate and store the trading thresholds to the portfolio.
        """
        stock_a_training_prices = yf.download(self.stock_a_ticker,
                                              start=training_start_date,
                                              end=training_end_date)['Close']
        stock_b_training_prices = yf.download(self.stock_b_ticker,
                                              start=training_start_date,
                                              end=training_end_date)['Close']
        ratio = stock_a_training_prices / stock_b_training_prices

        mean = ratio.mean()
        std = ratio.std()

        long_stock_a_threshold = mean - 0.5 * std
        long_stock_b_threshold = mean + 0.5 * std

        self.long_stock_a_threshold = long_stock_a_threshold
        self.long_stock_b_threshold = long_stock_b_threshold

    def execute_trades(self, start_date: str, end_date: str):
        """
        Execute trades based on the trading thresholds.
        """
        self.trading_start_date = start_date
        self.trading_end_date = end_date
        stock_a_prices = yf.download(self.stock_a_ticker,
                                     start=start_date,
                                     end=end_date)['Close']
        stock_b_prices = yf.download(self.stock_b_ticker,
                                     start=start_date,
                                     end=end_date)['Close']
        ratio = stock_a_prices / stock_b_prices

        for it in range(len(ratio)):
            if self.position is None:
                if ratio.iloc[it] < self.long_stock_a_threshold:
                    self.position = 'long A short B'
                    self.stock_a = +self.position_limit / stock_a_prices.iloc[it]
                    self.stock_b = -self.position_limit / stock_b_prices.iloc[it]
                elif ratio.iloc[it] > self.long_stock_b_threshold:
                    self.position = 'short A long B'
                    self.stock_a = -self.position_limit / stock_a_prices.iloc[it]
                    self.stock_b = +self.position_limit / stock_b_prices.iloc[it]
            elif self.position == 'short A long B' and ratio.iloc[it] < self.long_stock_a_threshold:
                # Flip postion from short A long B to long A short B
                # Sell B and buy A
                self.cash += self.stock_a * stock_a_prices.iloc[it]
                self.cash += self.stock_b * stock_b_prices.iloc[it]
                self.stock_a = +self.position_limit / stock_a_prices.iloc[it]
                self.stock_b = -self.position_limit / stock_b_prices.iloc[it]
                self.position = 'long A short B'
            elif self.position == 'long A short B' and ratio.iloc[it] > self.long_stock_b_threshold:
                # Flip postion from long A short B to short A long B
                # Sell A and buy B
                self.cash += self.stock_a * stock_a_prices.iloc[it]
                self.cash += self.stock_b * stock_b_prices.iloc[it]
                self.stock_a = -self.position_limit / stock_a_prices.iloc[it]
                self.stock_b = +self.position_limit / stock_b_prices.iloc[it]
                self.position = 'short A long B'
            self.update_over_time_values()

    def update_over_time_values(self):
        """
        Update the portfolio over time.
        """
        self.cash_over_time.append(self.cash)
        self.stock_a_over_time.append(self.stock_a)
        self.stock_b_over_time.append(self.stock_b)
        self.position_over_time.append(self.position)

def read_csv_file(filename: str):
    """
    Read a CSV file and return a list pandas dataframe object.

    Parameters
    ----------

    filename : str
        The filename to read.
        It can be one of the following:
        - "Price Data - CSV - Formation Period excl 2020.csv"
        - "Price Data - CSV - Formation Period=2020.csv"
        - "Price Data - CSV - Full Periods.csv"
        - "Price Data - CSV - Trading Period.csv"
    """

    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, '..', 'data')
    filepath = os.path.join(data_dir, filename)
    data = pd.read_csv(filepath)

    return data

def run_pairs_trade_strategy(stock_a_ticker: str = 'AAPL',
                             stock_b_ticker: str = 'MSFT',
                             training_start_date: str = '2019-01-01',
                             training_end_date: str = '2021-01-01',
                             testing_start_date: str = '2021-01-02',
                             testing_end_date: str = '2022-01-01'):
    """
    Run the pairs trading strategy.
    """

    portfolio = Portfolio(stock_a_ticker, stock_b_ticker)
    portfolio.calculate_trading_thresholds(training_start_date, training_end_date)
    portfolio.execute_trades(testing_start_date, testing_end_date)

    return portfolio
