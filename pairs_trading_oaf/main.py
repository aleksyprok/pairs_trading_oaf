"""
Main module for initialising and executing pairs trades.

Note that postition limit gives the maximum position size for each stock in the pair in USD.

We assume that only three possible positions are allowed:
- long stock A short stock B
- long stock B short stock A
- no position

When we long stock A and short stock B, we buy position_limit worth of stock A and short
position_limit worth of stock B and vice versa when we long stock B and short stock A.
"""

from pairs_trading_oaf import trading
from pairs_trading_oaf import portfolio
from pairs_trading_oaf import strategies

TRAINING_DATA_FNAME = "Price Data - CSV - Formation Period.csv"
TESTING_DATA_FNAME = "Price Data - CSV - Trading Period.csv"
POSITION_LIMIT = int(1e6) # 1 million USD
stock_pair_labels_list = [
    ("Microsoft Corporation (NasdaqGS:MSFT)", "Apple Inc. (NasdaqGS:AAPL)"),
    ("Bank of America Corporation (NYSE:BAC)", "JPMorgan Chase & Co. (NYSE:JPM)"),
]

master_portfolio = portfolio.MasterPortfolio(POSITION_LIMIT,
                                             TRAINING_DATA_FNAME,
                                             TESTING_DATA_FNAME)
for stock_pair_labels in stock_pair_labels_list:
    pair_portfolio = \
        portfolio.PairPortfolio(stock_pair_labels,
                                strategies.StrategyA,
                                master_portfolio)
    master_portfolio.add_pair_portfolio(pair_portfolio)

trading.simulate_trading(master_portfolio)
