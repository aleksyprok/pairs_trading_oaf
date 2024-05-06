"""
This file is used to create the CSV files for the ETFs price data.
The ETFs are fetched from Yahoo Finance using the yfinance library.
The ETFs are fetched for two periods: the initial period (formation period) and the trading period.
The data is then saved to CSV files for further use in the analysis.
"""

import yfinance as yf

etfs = {
    'SPY': 'SPDR S&P 500 ETF Trust (NYSE Arca:SPY)',
    'IVV': 'iShares Core S&P 500 ETF (NYSE Arca:IVV)',
    'VNQ': 'Vanguard Real Estate ETF (NYSE Arca:VNQ)',
    'IYR': 'iShares U.S. Real Estate ETF (NYSE Arca:IYR)',
    'EFA': 'iShares MSCI EAFE ETF (NYSE Arca:EFA)',
    'VEA': 'Vanguard FTSE Developed Markets ETF (NYSE Arca:VEA)',
    'XLE': 'Energy Select Sector SPDR Fund (NYSE Arca:XLE)',
    'OIH': 'VanEck Oil Services ETF (NYSE Arca:OIH)',
    'GLD': 'SPDR Gold Trust (NYSE Arca:GLD)',
    'SLV': 'iShares Silver Trust (NYSE Arca:SLV)'
}

# Formation period
START_DATE_INITIAL = '2010-01-04'
END_DATE_INITIAL = '2020-12-31'
data_initial = yf.download(list(etfs.keys()),
                           start=START_DATE_INITIAL,
                           end=END_DATE_INITIAL)['Adj Close']
data_initial.rename(columns=etfs, inplace=True)
data_initial.reset_index(inplace=True)
data_initial.rename(columns={'Date': 'Closing Date'}, inplace=True)
CSV_FILE_PATH_INITIAL = 'Price Data - CSV - Formation Period - ETF.csv'
data_initial.to_csv(CSV_FILE_PATH_INITIAL, index=False)

# Trading period
START_DATE_TRADING = '2021-01-04'
END_DATE_TRADING = '2023-06-30'
data_trading = yf.download(list(etfs.keys()),
                           start=START_DATE_TRADING,
                           end=END_DATE_TRADING)['Adj Close']

data_trading.rename(columns=etfs, inplace=True)
data_trading.reset_index(inplace=True)
data_trading.rename(columns={'Date': 'Closing Date'}, inplace=True)
CSV_FILE_PATH_TRADING = 'Price Data - CSV - Trading Period - ETF.csv'
data_trading.to_csv(CSV_FILE_PATH_TRADING, index=False)
