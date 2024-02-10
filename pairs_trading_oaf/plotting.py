"""
Functions to plot trading data.
"""

import os
import matplotlib.pyplot as plt
import numpy as np

def plot_average_values_over_time(master_portfolio):
    """
    Plots the average value of the portfolio over time for each pair
    in the master portfolio over the entire trading period.
    """
    current_dir = os.path.dirname(__file__)
    plots_dir = os.path.join(current_dir, '..', 'plots', master_portfolio.name)
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
                f'{master_portfolio.position_limit:.2f})')
        plt.xticks(rotation=45)
        ax.set_title(f'{master_portfolio.name} Average {value_string} over time')
        ax.legend()
        fname = os.path.join(plots_dir, 'average_' + value_string + '_over_time.png')
        fig.savefig(fname, dpi=300, bbox_inches='tight')
        plt.close()

def plot_values_over_time(master_portfolio):
    """
    Plots the values of the portfolio over time for each pair.
    """
    current_dir = os.path.dirname(__file__)
    plots_dir = os.path.join(current_dir, '..', 'plots', master_portfolio.name)
    master_portfolio.calc_strategy_strings()
    pairs_portfolio_index_dict = master_portfolio.calc_pairs_portfolio_index_dict()
    value_strings = ["portfolio_value", "cash", "ratio"]
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
                          f'{master_portfolio.position_limit:.2f})')
            plt.xticks(rotation=45)
            ax.set_title(f'{value_string} over time for stock pair {stock_pair_label}')
            ax.legend()
            plots_subdir = os.path.join(plots_dir, value_string + '_over_time')
            os.makedirs(plots_subdir, exist_ok=True)
            fname = os.path.join(plots_subdir, value_string + '_over_time_' +
                                 stock_pair_label + '.png')
            fig.savefig(fname, dpi=300, bbox_inches='tight')
            plt.close()

def plot_position_over_time(master_portfolio):
    """
    The position can be one of the following values:
    - "no position"
    - "long A short B"
    - "long B short A"
    """
    current_dir = os.path.dirname(__file__)
    plots_dir = os.path.join(current_dir, '..', 'plots', master_portfolio.name)
    os.makedirs(plots_dir, exist_ok=True)
    master_portfolio.calc_strategy_strings()
    pairs_portfolio_index_dict = master_portfolio.calc_pairs_portfolio_index_dict()
    stock_pair_labels = pairs_portfolio_index_dict[master_portfolio.strategy_strings[0]].keys()
    for stock_pair_label in stock_pair_labels:
        fig, ax = plt.subplots()
        for strategy_string in master_portfolio.strategy_strings:
            pairs_portfolio_index = \
                pairs_portfolio_index_dict[strategy_string][stock_pair_label]
            pair_portfolio = master_portfolio.pair_portfolios[pairs_portfolio_index]
            postion_over_time_int = \
                (1 * (np.array(pair_portfolio.position_over_time) == "long A short B")) -\
                (1 * (np.array(pair_portfolio.position_over_time) == "long B short A"))
            ax.scatter(pair_portfolio.dates_over_time,
                       postion_over_time_int,
                       s = 0.1,
                       label=strategy_string)
        ax.set_ylabel('Position (Position limit = $' +
                      f'{master_portfolio.position_limit:.2f})')
        ax.set_yticks([-1, 0, 1])
        ax.set_yticklabels(["long B short A", "no position", "long A short B"])
        plt.xticks(rotation=45)
        ax.set_title(f'Position over time for stock pair {stock_pair_label}')
        ax.legend()
        plot_subdir = os.path.join(plots_dir, 'position_over_time')
        os.makedirs(plot_subdir, exist_ok=True)
        fname = os.path.join(plot_subdir, 'position_over_time_' +
                             stock_pair_label + '.png')
        fig.savefig(fname, dpi=300, bbox_inches='tight')
        plt.close()

def plot_strategy_c_bollinger_bands_and_trades(master_portfolio):
    """
    Plots the Bollinger bands and annotates the trades for Strategy C
    """

    current_dir = os.path.dirname(__file__)
    plots_dir = os.path.join(current_dir, '..', 'plots', master_portfolio.name)
    os.makedirs(plots_dir, exist_ok=True)
    master_portfolio.calc_strategy_strings()
    pairs_portfolio_index_dict = master_portfolio.calc_pairs_portfolio_index_dict()
    stock_pair_labels = pairs_portfolio_index_dict[master_portfolio.strategy_strings[0]].keys()

    for stock_pair_label in stock_pair_labels:
        pairs_portfolio_index = pairs_portfolio_index_dict["StrategyC"][stock_pair_label]
        pair_portfolio = master_portfolio.pair_portfolios[pairs_portfolio_index]

        fig, ax = plt.subplots(figsize=(12, 7))
        ax.plot(pair_portfolio.dates_over_time, pair_portfolio.ratio_over_time,
                label="Ratio over time")

        band_color = 'skyblue'
        ax.plot(pair_portfolio.dates_over_time, pair_portfolio.strategy.upper_band_over_time,
                label="Upper Bollinger Band", color=band_color)
        ax.plot(pair_portfolio.dates_over_time, pair_portfolio.strategy.lower_band_over_time,
                label="Lower Bollinger Band", color=band_color)

        cash_delta = np.diff(pair_portfolio.cash_over_time,
                             prepend=pair_portfolio.cash_over_time[0])

        for i, delta in enumerate(cash_delta):
            if delta != 0:
                color = 'green' if delta > 0 else 'red'

                position = pair_portfolio.position_over_time[i]
                delta_text = f'{position}\nΔ${delta:.2f}'

                ax.annotate(delta_text,
                            xy=(pair_portfolio.dates_over_time[i],
                                pair_portfolio.ratio_over_time[i]),
                            xytext=(0, 10), textcoords='offset points',
                            arrowprops=dict(arrowstyle="->", color=color),
                            ha='center', va='bottom', color=color)

        ax.set_ylabel(f'Ratio of the pair {stock_pair_label}')
        plt.xticks(rotation=45)
        ax.set_title(f'StrategyC Bollinger Bands and Trades for Stock Pair {stock_pair_label}')
        ax.legend()

        plot_subdir = os.path.join(plots_dir, 'strategy_c_bollinger_bands_and_trades')
        os.makedirs(plot_subdir, exist_ok=True)
        fname = os.path.join(plot_subdir,
                             f'strategy_c_bollinger_bands_and_trades_{stock_pair_label}.png')
        fig.savefig(fname, dpi=300, bbox_inches='tight')
        plt.close()
