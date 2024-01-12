"""
Functions to plot trading data.
"""

import os
import matplotlib.pyplot as plt

def plot_average_values_over_time(master_portfolio):
    """
    Plots the average value of the portfolio over time for each pair
    in the master portfolio over the entire trading period.
    """
    current_dir = os.path.dirname(__file__)
    plots_dir = os.path.join(current_dir, '..', 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    master_portfolio.calc_strategy_strings()
    master_portfolio.calc_average_values_over_time_by_strategy()
    for value_string in master_portfolio.average_values_over_time.keys():
        fig, ax = plt.subplots()
        for strategy_string in master_portfolio.average_values_over_time[value_string].keys():
            ax.plot(master_portfolio.pair_portfolios[0].dates_over_time,
                    master_portfolio.average_values_over_time[value_string][strategy_string],
                    label=strategy_string)
        ax.set_ylabel(value_string + ' [USD] (Position limit = $' +
                f'{int(master_portfolio.position_limit):d})')
        plt.xticks(rotation=45)
        ax.set_title(f'Average {value_string} over time')
        ax.legend()
        fname = os.path.join(plots_dir, 'average_' + value_string + '_over_time.png')
        fig.savefig(fname, dpi=300, bbox_inches='tight')
        plt.close()

def plot_values_over_time(master_portfolio):
    """
    Plots the values of the portfolio over time for each pair.
    """
    current_dir = os.path.dirname(__file__)
    plots_dir = os.path.join(current_dir, '..', 'plots')
    master_portfolio.calc_strategy_strings()
    pairs_portfolio_index_dict = master_portfolio.calc_pairs_portfolio_index_dict()
    value_strings = ["portfolio_value", "cash"]
    stock_pair_labels = pairs_portfolio_index_dict[master_portfolio.strategy_strings[0]].keys()
    for value_string in value_strings:
        for stock_pair_label in stock_pair_labels:
            fig, ax = plt.subplots()
            for strategy_string in master_portfolio.strategy_strings:
                pairs_portfolio_index = \
                    pairs_portfolio_index_dict[strategy_string][stock_pair_label]
                pair_portfolio = master_portfolio.pair_portfolios[pairs_portfolio_index]
                ax.plot(pair_portfolio.dates_over_time,
                        pair_portfolio.__dict__[value_string + "_over_time"],
                        label=strategy_string)
            ax.set_ylabel(value_string + ' [USD] (Position limit = $' +
                          f'{int(master_portfolio.position_limit):d})')
            plt.xticks(rotation=45)
            ax.set_title(f'{value_string} over time for stock pair {stock_pair_label}')
            ax.legend()
            plots_subdir = os.path.join(plots_dir, value_string + '_over_time')
            os.makedirs(plots_subdir, exist_ok=True)
            fname = os.path.join(plots_subdir, value_string + '_over_time_' +
                                 stock_pair_label + '.png')
            fig.savefig(fname, dpi=300, bbox_inches='tight')
            plt.close()
