"""
Main module for pairs trading strategy.
"""
import matplotlib.pyplot as plt
import pairs_trading_oaf.trading as trading
import pairs_trading_oaf.plotting as plotting

STOCK_A_TICKER = 'AAPL'
STOCK_B_TICKER = 'MSFT'
TRAINING_START_DATE = '2010-01-01'
TRAINING_END_DATE = '2015-01-01'
TESTING_START_DATE = '2015-01-02'
TESTING_END_DATE = '2022-01-01'
portfolio = trading.run_pairs_trade_strategy(stock_a_ticker = STOCK_A_TICKER,
                                             stock_b_ticker = STOCK_B_TICKER,
                                             training_start_date = TRAINING_START_DATE,
                                             training_end_date = TRAINING_END_DATE,
                                             testing_start_date = TESTING_START_DATE,
                                             testing_end_date = TESTING_END_DATE)
plotting.plot_price_series(STOCK_A_TICKER, STOCK_B_TICKER,
                           TRAINING_START_DATE, TRAINING_END_DATE,
                           TESTING_START_DATE, TESTING_END_DATE)
plotting.plot_ratio_series(STOCK_A_TICKER, STOCK_B_TICKER,
                           TRAINING_START_DATE, TRAINING_END_DATE,
                           TESTING_START_DATE, TESTING_END_DATE,
                           long_stock_a_threshold = portfolio.long_stock_a_threshold,
                           long_stock_b_threshold = portfolio.long_stock_b_threshold)
plotting.plot_pnl(portfolio)
plt.show()
