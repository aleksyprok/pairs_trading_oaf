import yfinance as yf
import pandas as pd
import numpy as np

# Fetch historical data for MSFT and AAPL
msft = yf.download('MSFT', start='2020-01-01', end='2023-01-01')['Close']
aapl = yf.download('AAPL', start='2020-01-01', end='2023-01-01')['Close']

# Calculate the ratio of the two stocks
ratio = msft / aapl

# Define thresholds for buying and selling
mean = ratio.mean()
std = ratio.std()
sell_threshold = mean + 0.5 * std
buy_threshold = mean - 0.5 * std

# Initialize trade log and pnl
trade_log = pd.DataFrame(index=ratio.index, columns=['Position', 'PnL'])
pnl = 0
position = None  # 'long MSFT', 'long AAPL', or None

for i in range(1, len(ratio)):
    if position is None:
        if ratio.iloc[i] > sell_threshold:
            position = 'long AAPL'  # Buy AAPL, Sell MSFT
            entry_price_msft = msft.iloc[i]
            entry_price_aapl = aapl.iloc[i]
        elif ratio.iloc[i] < buy_threshold:
            position = 'long MSFT'  # Buy MSFT, Sell AAPL
            entry_price_msft = msft.iloc[i]
            entry_price_aapl = aapl.iloc[i]

    elif position == 'long MSFT' and ratio.iloc[i] <= mean:
        # Close position
        pnl += ((msft.iloc[i] - entry_price_msft) / entry_price_msft - 
                (aapl.iloc[i] - entry_price_aapl) / entry_price_aapl) * 100
        position = None

    elif position == 'long AAPL' and ratio.iloc[i] >= mean:
        # Close position
        pnl += ((aapl.iloc[i] - entry_price_aapl) / entry_price_aapl - 
                (msft.iloc[i] - entry_price_msft) / entry_price_msft) * 100
        position = None

    trade_log.at[trade_log.index[i], 'Position'] = position
    trade_log.at[trade_log.index[i], 'PnL'] = pnl

# Display final PnL
print(f"Total PnL: {pnl}%")
