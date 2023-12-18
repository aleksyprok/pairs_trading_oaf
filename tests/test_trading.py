"""
Test the functions in src/trading.py
"""

import src.trading as trading

def test_run_pairs_trade_strategy_defaults():
    """
    Test the run_pairs_trade_strategy function with default parameters.
    """
    result = trading.run_pairs_trade_strategy()
    assert result == 1, "Expected the function to return 1"

def test_run_pairs_trade_strategy_custom_tickers():
    """
    Test the run_pairs_trade_strategy function with custom ticker parameters.
    """
    custom_ticker_a = "GOOGL"
    custom_ticker_b = "TSLA"
    result = trading.run_pairs_trade_strategy(stock_a_ticker=custom_ticker_a,
                                              stock_b_ticker=custom_ticker_b)
    assert result == 1, "Expected the function to return 1"