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

def calculate_transaction_fee(trade_amount, trading_fee=0.0):
    """
    Calculate the transaction fee based on the trade amount.
    Fee is 0.1% of the trade amount.
    """
    return trade_amount * trading_fee

def close_position(pair_portfolio):
    """
    Close the current position.
    """
    total_value = pair_portfolio.shares[0] * pair_portfolio.stock_pair_prices[0] \
                + pair_portfolio.shares[1] * pair_portfolio.stock_pair_prices[1]
    transaction_fee = calculate_transaction_fee(total_value, trading_fee=pair_portfolio.trading_fee)
    pair_portfolio.cash = pair_portfolio.cash + total_value - transaction_fee
    pair_portfolio.shares = (0, 0)

def open_position(pair_portfolio, new_position):
    """
    Open a new position.
    """
    pair_portfolio.position = new_position
    if new_position == "no position":
        close_position(pair_portfolio)
    else:
        if new_position == "long A short B":
            shares_to_trade = (+pair_portfolio.position_limit /
                               pair_portfolio.stock_pair_prices[0],
                               -pair_portfolio.position_limit /
                               pair_portfolio.stock_pair_prices[1])
        elif new_position == "long B short A":
            shares_to_trade = (-pair_portfolio.position_limit /
                               pair_portfolio.stock_pair_prices[0],
                               +pair_portfolio.position_limit /
                               pair_portfolio.stock_pair_prices[1])
        
        total_value = abs(shares_to_trade[0]) * pair_portfolio.stock_pair_prices[0] \
                    + abs(shares_to_trade[1]) * pair_portfolio.stock_pair_prices[1]
        transaction_fee = calculate_transaction_fee(total_value, trading_fee=pair_portfolio.trading_fee)
        pair_portfolio.cash -= transaction_fee
        pair_portfolio.shares = shares_to_trade
