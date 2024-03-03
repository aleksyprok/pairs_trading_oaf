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
from pairs_trading_oaf import trading, portfolio, strategies, plotting

tic = time.perf_counter()

TRAINING_DATA_FNAMES = ["Price Data - CSV - Formation Period - Crypto.csv",
                        "Price Data - CSV - Formation Period - ETF.csv",
                        "Price Data - CSV - Formation Period.csv"]
TESTING_DATA_FNAMES = ["Price Data - CSV - Trading Period - Crypto.csv",
                       "Price Data - CSV - Trading Period - ETF.csv",
                       "Price Data - CSV - Trading Period.csv"]
TRADING_FEE = 0.0002
INITIAL_CASH = 1
POSITION_LIMIT = INITIAL_CASH * 0.3

stock_pair_labels_list_of_lists = []
stock_pair_labels_list = [("Bitcoin (:BTC)", "Ethereum (:ETH)")]
stock_pair_labels_list_of_lists.append(stock_pair_labels_list)
stock_pair_labels_list = [
    ("iShares MSCI EAFE ETF (NYSE Arca:EFA)", "SPDR Gold Trust (NYSE Arca:GLD)"),
    ("iShares Core S&P 500 ETF (NYSE Arca:IVV)", "iShares U.S. Real Estate ETF (NYSE Arca:IYR)"),
    ("VanEck Oil Services ETF (NYSE Arca:OIH)", "iShares Silver Trust (NYSE Arca:SLV)"),
    ("SPDR S&P 500 ETF Trust (NYSE Arca:SPY)",
     "Vanguard FTSE Developed Markets ETF (NYSE Arca:VEA)"),
    ("Vanguard Real Estate ETF (NYSE Arca:VNQ)", "Energy Select Sector SPDR Fund (NYSE Arca:XLE)"),
]
stock_pair_labels_list_of_lists.append(stock_pair_labels_list)
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
stock_pair_labels_list_of_lists.append(stock_pair_labels_list)
master_portfolio_names = ["Crypto", "ETFs", "Stocks"]

for i, stock_pair_labels_list in enumerate(stock_pair_labels_list_of_lists):
    stock_pair_labels_list = stock_pair_labels_list_of_lists[i]
    TRAINING_DATA_FNAME = TRAINING_DATA_FNAMES[i]
    TESTING_DATA_FNAME = TESTING_DATA_FNAMES[i]
    master_portfolio = portfolio.MasterPortfolio(POSITION_LIMIT,
                                                 TRAINING_DATA_FNAME,
                                                 TESTING_DATA_FNAME,
                                                 trading_fee=TRADING_FEE,
                                                 name=master_portfolio_names[i])
    for StrategyClass in [strategies.StrategyA, strategies.StrategyB, strategies.StrategyC]:
        for stock_pair_labels in stock_pair_labels_list:
            pair_portfolio = \
                portfolio.PairPortfolio(stock_pair_labels,
                                        StrategyClass,
                                        master_portfolio,
                                        cash=INITIAL_CASH)
            master_portfolio.add_pair_portfolio(pair_portfolio)

    trading.simulate_trading(master_portfolio)

    plotting.plot_average_values_over_time(master_portfolio)
    plotting.plot_values_over_time(master_portfolio)
    plotting.plot_position_over_time(master_portfolio)
    plotting.plot_strategy_c_bollinger_bands_and_trades(master_portfolio)
    plotting.plot_strategy_b_macd_histogram_and_trades(master_portfolio)

toc = time.perf_counter()
print(f"Time taken: {toc - tic:0.4f} seconds")
