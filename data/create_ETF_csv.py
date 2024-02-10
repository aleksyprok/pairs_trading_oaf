import yfinance as yf
import pandas as pd

# Define the ETFs and their formatted names
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

start_date = '2010-01-04'
end_date = '2020-12-31'

# Fetching the data
data = yf.download(list(etfs.keys()), start=start_date, end=end_date)['Adj Close']

# Reformatting column names
data.rename(columns=etfs, inplace=True)

# Reformatting the data to match the desired format
data.reset_index(inplace=True)
data.rename(columns={'Date': 'Closing Date'}, inplace=True)

# Save the data to a CSV file
csv_file_path = 'Price Data - CSV - Formation Period - ETF.csv'
data.to_csv(csv_file_path, index=False)
