"""
This script reads the cryptocurrency data from the CSV files, preprocesses it,
and saves the data for the formation and trading periods.
"""

from datetime import datetime
import pandas as pd

def format_date(date_str):
    """
    Convert the date from the format 'dd/mm/yyyy hh:mm' to 'yyyy-mm-dd'.
    """
    return datetime.strptime(date_str, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d')

def read_and_preprocess(file_name):
    """
    Read the data from the CSV file and preprocess it.
    """
    df = pd.read_csv(file_name)
    df.drop('symbol', axis=1, inplace=True)
    df['date'] = df['date'].apply(format_date)
    df.set_index('date', inplace=True)
    return df

btc_df = read_and_preprocess('BTCUSD_day.csv')
eth_df = read_and_preprocess('ETHUSD_day.csv')

btc_df.rename(columns={'open_price': 'Bitcoin (:BTC_over_USD)'}, inplace=True)
eth_df.rename(columns={'open_price': 'Ethereum (:ETH_over_USD)'}, inplace=True)

merged_df = btc_df.join(eth_df, how='outer')

def save_period_data(start_date, end_date, file_name):
    """
    Save the data for the specified period to a CSV file.
    """
    period_df = merged_df.loc[start_date:end_date].copy()
    period_df.reset_index(inplace=True)
    period_df.rename(columns={'index': 'Closing Date'}, inplace=True)
    period_df.to_csv(file_name, index=False)

save_period_data('2016-03-09', '2020-12-30', 'Price Data - CSV - Formation Period - Crypto.csv')
save_period_data('2021-01-04', '2023-06-29', 'Price Data - CSV - Trading Period - Crypto.csv')
