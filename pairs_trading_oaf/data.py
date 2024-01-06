"""
This module contains functions to read data.
"""
import os
import pandas as pd

def read_csv(filename: str):
    """
    Read a CSV file and return a pandas dataframe object and set the index to be the
    'Closing Date' column.

    Parameters
    ----------

    filename : str
        The filename to read.
        It can be one of the following:
        - "Price Data - CSV - Formation Period excl 2020.csv"
        - "Price Data - CSV - Formation Period.csv"
        - "Price Data - CSV - Full Periods.csv"
        - "Price Data - CSV - Trading Period.csv"
    """

    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, '..', 'data')
    filepath = os.path.join(data_dir, filename)

    data = pd.read_csv(filepath)

    # Assuming the first column is 'Closing Date'
    data = pd.read_csv(filepath, index_col=0, parse_dates=True)

    return data
