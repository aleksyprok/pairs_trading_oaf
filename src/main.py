# import yfinance as yf
# import pandas as pd

# def fetch_data(symbol, start_date, end_date):
#     return yf.download(symbol, start=start_date, end=end_date)['Close']

# def calculate_ratio(stock_a, stock_b):
#     return stock_a / stock_b

# def execute_strategy(ratio):
#     mean = ratio.mean()
#     std = ratio.std()
#     sell_threshold = mean + 0.5 * std
#     buy_threshold = mean - 0.5 * std

#     trade_log = pd.DataFrame(index=ratio.index, columns=['Position', 'PnL'])
#     pnl = 0
#     position = None  # 'long MSFT', 'long AAPL', or None

#     for i in range(1, len(ratio)):
#         if position is None:
#             if ratio.iloc[i] > sell_threshold:
#                 position = 'long AAPL'
#                 entry_price_msft = msft.iloc[i]
#                 entry_price_aapl = aapl.iloc[i]
#             elif ratio.iloc[i] < buy_threshold:
#                 position = 'long MSFT'
#                 entry_price_msft = msft.iloc[i]
#                 entry_price_aapl = aapl.iloc[i]
#         elif position == 'long MSFT' and ratio.iloc[i] <= mean:
#             pnl += ((msft.iloc[i] - entry_price_msft) / entry_price_msft -
#                     (aapl.iloc[i] - entry_price_aapl) / entry_price_aapl) * 100
#             position = None
#         elif position == 'long AAPL' and ratio.iloc[i] >= mean:
#             pnl += ((aapl.iloc[i] - entry_price_aapl) / entry_price_aapl -
#                     (msft.iloc[i] - entry_price_msft) / entry_price_msft) * 100
#             position = None

#         trade_log.at[trade_log.index[i], 'Position'] = position
#         trade_log.at[trade_log.index[i], 'PnL'] = pnl

#     return pnl, trade_log

# Calculate ratio
# If ratio > threshold:
# Short A and long B
# If ratio < threshhold:
# Long A and short B
# Possible positions = [None, "long A short B", "short A long B" 

# # Example usage
# msft = fetch_data('MSFT', '2020-01-01', '2023-01-01')
# aapl = fetch_data('AAPL', '2020-01-01', '2023-01-01')
# ratio = calculate_ratio(msft, aapl)
# pnl, trade_log = execute_strategy(ratio)
# print(f"Total PnL: {pnl}%")
