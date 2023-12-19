"""
Functions to execute pairs trading strategy.
"""

import yfinance as yf

def run_pairs_trade_strategy(stock_a_ticker: str = 'AAPL',
                             stock_b_ticker: str = 'MSFT',
                             training_start_date: str = '2019-01-01',
                             training_end_date: str = '2021-01-01',
                             testing_start_date: str = '2021-01-02',
                             testing_end_date: str = '2021-06-01'):
    print(stock_a_ticker)
    print(stock_b_ticker)
    return 1
