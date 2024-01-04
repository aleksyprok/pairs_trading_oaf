"""
Functions to plot trading data.
"""

import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf

def plot_price_series(stock_a_ticker: str, stock_b_ticker: str,
                      training_start_date: str, training_end_date: str,
                      testing_start_date: str, testing_end_date: str):
    """
    Plots the price series for two tickers.
    """
    stock_a_prices_training = yf.download(stock_a_ticker,
                                          start=training_start_date,
                                          end=training_end_date)['Close']
    stock_b_prices_training = yf.download(stock_b_ticker,
                                          start=training_start_date,
                                          end=training_end_date)['Close']
    stock_a_prices_testing = yf.download(stock_a_ticker,
                                         start=testing_start_date,
                                         end=testing_end_date)['Close']
    stock_b_prices_testing = yf.download(stock_b_ticker,
                                         start=testing_start_date,
                                         end=testing_end_date)['Close']

    fig, ax = plt.subplots()
    fig_size = fig.get_size_inches()
    fig.set_size_inches(fig_size[0], fig_size[1])

    ax.plot(stock_a_prices_training.index, stock_a_prices_training,
            label=f'{stock_a_ticker} Training')
    ax.plot(stock_b_prices_training.index, stock_b_prices_training,
            label=f'{stock_b_ticker} Training')
    ax.plot(stock_a_prices_testing.index, stock_a_prices_testing,
            label=f'{stock_a_ticker} Testing')
    ax.plot(stock_b_prices_testing.index, stock_b_prices_testing,
            label=f'{stock_b_ticker} Testing')

    ax.set_ylabel('Price')
    ax.legend()
    plt.xticks(rotation=45)

def plot_ratio_series(stock_a_ticker: str, stock_b_ticker: str,
                      training_start_date: str, training_end_date: str,
                      testing_start_date: str, testing_end_date: str,
                      long_stock_a_threshold=None, long_stock_b_threshold=None):
    """
    Plots the ratio series for two tickers.
    """
    stock_a_prices_training = yf.download(stock_a_ticker,
                                          start=training_start_date,
                                          end=training_end_date)['Close']
    stock_b_prices_training = yf.download(stock_b_ticker,
                                          start=training_start_date,
                                          end=training_end_date)['Close']
    stock_a_prices_testing = yf.download(stock_a_ticker,
                                         start=testing_start_date,
                                         end=testing_end_date)['Close']
    stock_b_prices_testing = yf.download(stock_b_ticker,
                                         start=testing_start_date,
                                         end=testing_end_date)['Close']

    ratio_training = stock_a_prices_training / stock_b_prices_training
    ratio_testing = stock_a_prices_testing / stock_b_prices_testing

    fig, ax = plt.subplots()
    fig_size = fig.get_size_inches()
    fig.set_size_inches(fig_size[0], fig_size[1])

    ax.plot(ratio_training.index, ratio_training, label='Training')
    ax.plot(ratio_testing.index, ratio_testing, label='Testing')

    if long_stock_a_threshold is not None:
        ax.axhline(long_stock_a_threshold, color='r', linestyle='--',
                   label=f'Long {stock_a_ticker} Threshold')
    if long_stock_b_threshold is not None:
        ax.axhline(long_stock_b_threshold, color='g', linestyle='--',
                   label=f'Long {stock_b_ticker} Threshold')

    ax.set_ylabel(f'Ratio of {stock_a_ticker} over {stock_b_ticker} prices')
    ax.legend()
    plt.xticks(rotation=45)

def plot_pnl(portfolio):
    """
    Plots the profit and loss of the portfolio over time.
    """

    stock_a_prices = yf.download(portfolio.stock_a_ticker,
                                 start=portfolio.trading_start_date,
                                 end=portfolio.trading_end_date)['Close']
    stock_b_prices = yf.download(portfolio.stock_b_ticker,
                                 start=portfolio.trading_start_date,
                                 end=portfolio.trading_end_date)['Close']

    fig, ax = plt.subplots()
    fig_size = fig.get_size_inches()
    fig.set_size_inches(fig_size[0], fig_size[1])
    stock_a_portfolio_value = np.array(portfolio.stock_a_over_time) * np.array(stock_a_prices)
    stock_b_portfolio_value = np.array(portfolio.stock_b_over_time) * np.array(stock_b_prices)
    total_portfolio_value = portfolio.cash_over_time + stock_a_portfolio_value \
                          + stock_b_portfolio_value

    ax.plot(stock_a_prices.index, portfolio.cash_over_time, label='Cash')
    ax.plot(stock_a_prices.index,
            stock_a_portfolio_value,
            label='Stock A Holdings * Stock A Price')
    ax.plot(stock_a_prices.index,
            stock_b_portfolio_value,
            label='Stock B Holdings * Stock B Price')
    ax.plot(stock_a_prices.index, total_portfolio_value,
            label='Total')
    ax.set_ylabel('Value')
    ax.legend()
    plt.xticks(rotation=45)

def plot_pnl_over_time(master_portfolio):
    """
    Plots the profit and loss of the portfolio over time for each pair
    in the master portfolio over the entire trading period.
    """

    for pair_portfolio in master_portfolio.pair_portfolios:

        fig, ax = plt.subplots()
        fig_size = fig.get_size_inches()
        fig.set_size_inches(fig_size[0], fig_size[1])

        ax.plot(pair_portfolio.dates_over_time, pair_portfolio.cash_over_time)
        ax.set_ylabel('Cash')
        plt.xticks(rotation=45)
        ax.set_title(f'Cash over time for {pair_portfolio.stock_pair_labels[0]} and '
                     f'{pair_portfolio.stock_pair_labels[1]}')
