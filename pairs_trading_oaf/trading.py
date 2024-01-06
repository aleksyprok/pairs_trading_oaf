"""
Contains the routines for trading and updating the portfolios.
This module does not contain any strategy-specific code.
"""
from pairs_trading_oaf import data

def simulate_trading(master_portfolio):
    """
    Simulate trading for the master portfolio by iterating through the testing data.
    """

    df_test = data.read_csv(master_portfolio.testing_data_str)

    for date, row in df_test.iterrows():
        for pair_portfolio in master_portfolio.pair_portfolios:
            pair_portfolio.update_prices_and_date(date, row)
            new_position = pair_portfolio.strategy.calculate_new_position()
            execute_trades(pair_portfolio, new_position)
            pair_portfolio.update_over_time_values()

def execute_trades(pair_portfolio, new_position):
    """
    Execute trades at the end of the day based on the new position.
    """
    if new_position == pair_portfolio.position:
        # No change in position so do nothing
        return
    else:
        close_position(pair_portfolio)
        open_position(pair_portfolio, new_position)

def close_position(pair_portfolio):
    """
    Close the current position. This is done by selling/buying all shares of stock A and stock B
    until we own no shares of either stock.
    """
    pair_portfolio.cash = pair_portfolio.cash \
                        + pair_portfolio.shares[0] * pair_portfolio.stock_pair_prices[0] \
                        + pair_portfolio.shares[1] * pair_portfolio.stock_pair_prices[1]
    pair_portfolio.shares = (0, 0)

def open_position(pair_portfolio, new_position):
    """
    Open a new position. This is done by buying/selling all shares of stock A and stock B until
    we own/short the maximum number of shares of each stock.

    Note that we allow for the possibility of owning a fraction of a share of a stock.
    """
    pair_portfolio.position = new_position
    if new_position == "no position":
        close_position(pair_portfolio)
    elif new_position == "long A short B":
        pair_portfolio.shares = (+pair_portfolio.position_limit /
                                  pair_portfolio.stock_pair_prices[0],
                                 -pair_portfolio.position_limit /
                                  pair_portfolio.stock_pair_prices[1])
    elif new_position == "long B short A":
        pair_portfolio.shares = (-pair_portfolio.position_limit /
                                  pair_portfolio.stock_pair_prices[0],
                                 +pair_portfolio.position_limit /
                                  pair_portfolio.stock_pair_prices[1])
