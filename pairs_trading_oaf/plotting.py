"""
Functions to plot trading data.
"""

import matplotlib.pyplot as plt

def plot_pnl_over_time(master_portfolio):
    """
    Plots the profit and loss of the portfolio over time for each pair
    in the master portfolio over the entire trading period.
    """

    for pair_portfolio in master_portfolio.pair_portfolios:

        fig, ax = plt.subplots()
        fig_size = fig.get_size_inches()
        fig.set_size_inches(fig_size[0], fig_size[1])

        ax.plot(pair_portfolio.dates_over_time, pair_portfolio.cash_over_time)
        ax.set_ylabel('Cash')
        plt.xticks(rotation=45)
        ax.set_title(f'Cash over time for {pair_portfolio.stock_pair_labels[0]} and '
                     f'{pair_portfolio.stock_pair_labels[1]}')
