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

import time
# import matplotlib.pyplot as plt
from pairs_trading_oaf import trading, portfolio, strategies, plotting

tic = time.perf_counter()

TRAINING_DATA_FNAME = "Price Data - CSV - Formation Period.csv"
TESTING_DATA_FNAME = "Price Data - CSV - Trading Period.csv"
POSITION_LIMIT = int(1e0)

stock_pair_labels_list = [
    ("Microsoft Corporation (NasdaqGS:MSFT)", "Apple Inc. (NasdaqGS:AAPL)"),
    ("Bank of America Corporation (NYSE:BAC)", "JPMorgan Chase & Co. (NYSE:JPM)"),
    ("Exxon Mobil Corporation (NYSE:XOM)", "Chevron Corporation (NYSE:CVX)"),
    ("Walmart Inc. (NYSE:WMT)", "Target Corporation (NYSE:TGT)"),
    ("The Coca-Cola Company (NYSE:KO)", "PepsiCo, Inc. (NasdaqGS:PEP)"),
    ("Johnson & Johnson (NYSE:JNJ)", "Abbott Laboratories (NYSE:ABT)"),
    ("The Procter & Gamble Company (NYSE:PG)", "Unilever PLC (LSE:ULVR)"),
    ("The Boeing Company (NYSE:BA)", "Airbus SE (ENXTPA:AIR)"),
    ("Caterpillar Inc. (NYSE:CAT)", "Deere & Company (NYSE:DE)"),
    ("Wells Fargo & Company (NYSE:WFC)", "Citigroup Inc. (NYSE:C)"),
]
StrategyClass = strategies.StrategyB2

master_portfolio = portfolio.MasterPortfolio(POSITION_LIMIT,
                                             TRAINING_DATA_FNAME,
                                             TESTING_DATA_FNAME)
for stock_pair_labels in stock_pair_labels_list:
    pair_portfolio = \
        portfolio.PairPortfolio(stock_pair_labels,
                                StrategyClass,
                                master_portfolio)
    master_portfolio.add_pair_portfolio(pair_portfolio)

trading.simulate_trading(master_portfolio)

plotting.plot_portfolio_value_over_time(master_portfolio)

toc = time.perf_counter()
print(f"Time taken: {toc - tic:0.4f} seconds")

# plt.show()
