"""
Functions to plot trading data.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

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
                plt.grid(True)
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
    num_bins = 100

    for stock_pair_label in stock_pair_labels:
        pairs_portfolio_index = pairs_portfolio_index_dict["StrategyC"][stock_pair_label]
        pair_portfolio = master_portfolio.pair_portfolios[pairs_portfolio_index]

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.plot(pair_portfolio.dates_over_time[-num_bins:],
                pair_portfolio.ratio_over_time[-num_bins:],
                label="Ratio over time")

        band_color = 'skyblue'
        ax.plot(pair_portfolio.dates_over_time[-num_bins:],
                pair_portfolio.strategy.upper_band_over_time[-num_bins:],
                label="Bollinger Band", color=band_color)
        ax.legend()
        ax.plot(pair_portfolio.dates_over_time[-num_bins:],
                pair_portfolio.strategy.lower_band_over_time[-num_bins:],
                label="Lower Bollinger Band", color=band_color)

        cash_delta = np.diff(pair_portfolio.cash_over_time,
                             prepend=pair_portfolio.cash_over_time[0])

        for i, delta in enumerate(cash_delta[-num_bins:]):
            if delta != 0:
                color = 'green' if delta > 0 else 'red'

                position = pair_portfolio.position_over_time[-num_bins:][i]
                # delta_text = f'{position}\nΔ${delta:.2f}'
                delta_text = f'{position}'

                ax.annotate(delta_text,
                            xy=(pair_portfolio.dates_over_time[-num_bins:][i],
                                pair_portfolio.ratio_over_time[-num_bins:][i]),
                            xytext=(0, 90), textcoords='offset points',
                            arrowprops=dict(arrowstyle="->", color=color),
                            ha='center', va='bottom', color=color)

        # ax.set_ylabel(f'Ratio of the {stock_pair_label} prices')
        # Replace _ with / in stock pair label
        ax.set_ylabel(f'Pair price ratio ({stock_pair_label.replace("_", "/")})')
        # plt.xticks(rotation=45)
        ax.grid(True)
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[4, 5, 6, 7]))
        # ax.xaxis.set_major_locator(plt.MultipleLocator(5))
        # ax.set_title(f'StrategyC Bollinger Bands and Trades for Stock Pair {stock_pair_label}')

        plot_subdir = os.path.join(plots_dir, 'strategy_c_bollinger_bands_and_trades')
        os.makedirs(plot_subdir, exist_ok=True)
        fname = os.path.join(plot_subdir,
                             f'strategy_c_bollinger_bands_and_trades_{stock_pair_label}.png')
        fig.savefig(fname, dpi=1000, bbox_inches='tight')
        plt.close()

def plot_strategy_b_macd_histogram_and_trades(master_portfolio):
    """
    Plots the MACD histogram and annotates the trades for Strategy B
    """

    current_dir = os.path.dirname(__file__)
    plots_dir = os.path.join(current_dir, '..', 'plots', master_portfolio.name)
    os.makedirs(plots_dir, exist_ok=True)
    master_portfolio.calc_strategy_strings()
    pairs_portfolio_index_dict = master_portfolio.calc_pairs_portfolio_index_dict()
    stock_pair_labels = pairs_portfolio_index_dict[master_portfolio.strategy_strings[0]].keys()
    num_bins = 50

    for stock_pair_label in stock_pair_labels:
        pairs_portfolio_index = pairs_portfolio_index_dict["StrategyB"][stock_pair_label]
        pair_portfolio = master_portfolio.pair_portfolios[pairs_portfolio_index]

        # Figure needs to go in a powerpoint presentation on the right half of a 16:9 slide,
        # therefore the figsize is set to (5, 4)
        # The figure has two subplots, the top one shows the ratio over time
        # as well as the fast and slow ewma over time.
        # The bottom figure shows the MACD and the signal line over time.
        fig, axs = plt.subplots(2, 1, figsize=(8, 8), sharex=False)
        axs[0].plot(pair_portfolio.dates_over_time[-num_bins:],
                    pair_portfolio.ratio_over_time[-num_bins:],
                    label="Ratio over time")
        axs[0].plot(pair_portfolio.dates_over_time[-num_bins:],
                    pair_portfolio.strategy.over_time_vals.fast_ewma[-num_bins:],
                    label="Fast EWMA")
        axs[0].plot(pair_portfolio.dates_over_time[-num_bins:],
                    pair_portfolio.strategy.over_time_vals.slow_ewma[-num_bins:],
                    label="Slow EWMA")
        axs[0].set_ylabel(f'Ratio of {stock_pair_label} prices')
        cash_delta = np.diff(pair_portfolio.cash_over_time,
                             prepend=pair_portfolio.cash_over_time[0])
        for i, delta in enumerate(cash_delta[-num_bins:]):
            if delta != 0:
                color = 'green' if delta > 0 else 'red'
                position = pair_portfolio.position_over_time[-num_bins:][i]
                delta_text = f'{position}'
                axs[0].annotate(delta_text,
                                xy=(pair_portfolio.dates_over_time[-num_bins:][i],
                                    pair_portfolio.ratio_over_time[-num_bins:][i]),
                                xytext=(0, 60), textcoords='offset points',
                                arrowprops=dict(arrowstyle="->", color=color),
                                ha='center', va='bottom', color=color)
        axs[0].legend()

        axs[1].plot(pair_portfolio.dates_over_time[-num_bins:],
                    pair_portfolio.strategy.over_time_vals.macd[-num_bins:],
                    label="MACD")
        axs[1].plot(pair_portfolio.dates_over_time[-num_bins:],
                    pair_portfolio.strategy.over_time_vals.signal[-num_bins:],
                    label="Signal Line")
        # Add annotations for the trades
        cash_delta = np.diff(pair_portfolio.cash_over_time,
                             prepend=pair_portfolio.cash_over_time[0])
        for i, delta in enumerate(cash_delta[-num_bins:]):
            if delta != 0:
                color = 'green' if delta > 0 else 'red'
                position = pair_portfolio.position_over_time[-num_bins:][i]
                delta_text = f'{position}'
                axs[1].annotate(delta_text,
                                xy=(pair_portfolio.dates_over_time[-num_bins:][i],
                                    pair_portfolio.strategy.over_time_vals.macd[-num_bins:][i]),
                                xytext=(0, 60),
                                textcoords='offset points',
                                arrowprops=dict(arrowstyle="->", color=color),
                                ha='center', va='bottom', color=color)
        axs[1].set_ylabel('MACD & Signal')
        axs[1].legend()
        # Make x-axis labels more sparse
        # axs[0].xaxis.set_major_locator(plt.MaxNLocator(5))
        # axs[1].xaxis.set_major_locator(plt.MaxNLocator(5))
        # Change x-axis labels to just show year and month and at 1st of May, June
        # and July
        axs[0].xaxis.set_major_locator(mdates.MonthLocator(bymonth=[5, 6, 7]))
        axs[1].xaxis.set_major_locator(mdates.MonthLocator(bymonth=[5, 6, 7]))
        # axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        # axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        # axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        # plt.xticks(rotation=45)
        # Add grid to both axes
        for ax in axs:
            ax.grid(True)
        # Add more vertical grid lines
        for ax in axs:
            ax.grid(which='minor', axis='x', linestyle='-')
            ax.grid(which='major', axis='x', linestyle='-')
            ax.grid(which='minor', axis='y', linestyle='-')
            ax.grid(which='major', axis='y', linestyle='-')
            # Add more grid lines or xticks if needs be
            # Add more grid lines or xticks if needs be
        # Add more major grid lines to x-axis
        # Add more major grid lines to x-axis
        axs[0].xaxis.set_major_locator(plt.MultipleLocator(10))
        axs[1].xaxis.set_major_locator(plt.MultipleLocator(10))

        plot_subdir = os.path.join(plots_dir, 'strategy_b_macd_histogram_and_trades')
        os.makedirs(plot_subdir, exist_ok=True)
        fname = os.path.join(plot_subdir,
                             f'strategy_b_macd_histogram_and_trades_{stock_pair_label}.png')
        fig.savefig(fname, dpi=1000, bbox_inches='tight')
        plt.close()

def plot_strategy_b_against_d(master_portfolio):
    """
    Plot the MACD strategy (Strategy B) against Golden's cointigration strategy (Strategy D).
    For the following stock pairs:
    - JPM_BAC
    - WMT_TGT
    - CAT_DE
    - CVX_XOM
    """
    # stock_pair_labels = ["JPM_BAC", "WMT_TGT", "CAT_DE", "CVX_XOM"]
    stock_pair_labels = ["WMT_TGT", "CVX_XOM", "CAT_DE", "JPM_BAC"]
    clrs = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']
    master_portfolio.calc_strategy_strings()
    pairs_portfolio_index_dict = master_portfolio.calc_pairs_portfolio_index_dict()
    fig, ax = plt.subplots()
    for i, stock_pair_label in enumerate(stock_pair_labels):
        pairs_portfolio_index_b = pairs_portfolio_index_dict["StrategyB"][stock_pair_label]
        pairs_portfolio_index_d = pairs_portfolio_index_dict["StrategyD"][stock_pair_label]
        pair_portfolio_b = master_portfolio.pair_portfolios[pairs_portfolio_index_b]
        pair_portfolio_d = master_portfolio.pair_portfolios[pairs_portfolio_index_d]

        ax.plot(pair_portfolio_b.dates_over_time,
                np.array(pair_portfolio_b.cash_over_time) - pair_portfolio_b.cash_over_time[0],
                color = clrs[i],
                linestyle = '--')
        ax.plot(pair_portfolio_d.dates_over_time,
                np.array(pair_portfolio_d.cash_over_time) - pair_portfolio_d.cash_over_time[0],
                color = clrs[i],
                linestyle = '-')
    plt.grid(True)
    ax.set_ylabel('Cash')
    # Make custom legend
    for i, stock_pair_label in enumerate(stock_pair_labels):
        ax.plot([], [], color=clrs[i], label=stock_pair_label)
    ax.legend()
    strategies = ['Mean-reversion', 'MACD']
    linestyles = ['-', '--']
    for i, strategy in enumerate(strategies):
        linestyle = linestyles[i]
        ax.plot([], [], color='k', linestyle=linestyle, label=strategy)
    ax.legend()
    current_dir = os.path.dirname(__file__)
    plots_dir = os.path.join(current_dir, '..', 'plots', master_portfolio.name)
    os.makedirs(plots_dir, exist_ok=True)
    fname = os.path.join(plots_dir,
                         'strategy_b_against_d.png')
    fig.savefig(fname,
                dpi=300, bbox_inches='tight')

def make_csv_strategy_d_and_b(master_portfolio):
    """
    Make a CSV of cash everytime Strategy D or Strategy B closes a position with date as a column.
    Use Pandas dataframe to do this.
    """
    current_dir = os.path.dirname(__file__)
    plots_dir = os.path.join(current_dir, '..', 'plots', master_portfolio.name)
    os.makedirs(plots_dir, exist_ok=True)
    master_portfolio.calc_strategy_strings()
    pairs_portfolio_index_dict = master_portfolio.calc_pairs_portfolio_index_dict()
    for strategy_string in pairs_portfolio_index_dict.keys():
        for stock_pair_label in pairs_portfolio_index_dict[strategy_string].keys():
            pairs_portfolio_index = pairs_portfolio_index_dict[strategy_string][stock_pair_label]
            pair_portfolio = master_portfolio.pair_portfolios[pairs_portfolio_index]
            df = pd.DataFrame()
            df['date'] = pair_portfolio.dates_over_time
            df['cash'] = np.array(pair_portfolio.cash_over_time) - pair_portfolio.cash_over_time[0]
            df['position'] = pair_portfolio.position_over_time
            plot_subdir = os.path.join(plots_dir, strategy_string)
            os.makedirs(plot_subdir, exist_ok=True)
            fname = os.path.join(plot_subdir,
                                 f'{strategy_string}_{stock_pair_label}.csv')
            df.to_csv(fname)
            # Filter csv to only show the cash when the position changes because this is the
            # only time when the cash changes
            df = df[df['position'] != df['position'].shift(1)]
            fname = os.path.join(plot_subdir,
                                 f'{strategy_string}_{stock_pair_label}_filtered.csv')
            if strategy_string == "StrategyB":
                fname = os.path.join(plot_subdir,
                                     f'MACD_strategy_{stock_pair_label}_filtered.csv')
            elif strategy_string == "StrategyD":
                fname = os.path.join(plot_subdir,
                                     f'Mean-reversion_strategy_{stock_pair_label}_filtered.csv')
            df.to_csv(fname)
            # Plot the cash over time from filtered and non-filtered
            fig, ax = plt.subplots()
            ax.plot(pair_portfolio.dates_over_time,
                    np.array(pair_portfolio.cash_over_time) - pair_portfolio.cash_over_time[0],
                    label='All trades')
            ax.plot(df['date'], df['cash'], label='Filtered trades')
            ax.set_ylabel('Cash [USD]')
            plt.xticks(rotation=45)
            ax.set_title(f'Cash over time for {strategy_string} {stock_pair_label}')
            ax.legend()
            plot_subdir = os.path.join(plots_dir, 'cash_over_time')
            os.makedirs(plot_subdir, exist_ok=True)
            fname = os.path.join(plot_subdir,
                                 f'{strategy_string}_{stock_pair_label}_cash_over_time.png')
            fig.savefig(fname, dpi=300, bbox_inches='tight')
            plt.close()

def make_csv_position_strategy_b_d(master_portfolio):
    """
    Make a CSV of the total time a position is open, as well as the average time a position is held for. We need four numbers for each stock pair.
    """
    current_dir = os.path.dirname(__file__)
    plots_dir = os.path.join(current_dir, '..', 'plots', master_portfolio.name)
    os.makedirs(plots_dir, exist_ok=True)
    master_portfolio.calc_strategy_strings()
    pairs_portfolio_index_dict = master_portfolio.calc_pairs_portfolio_index_dict()
    with open(os.path.join(plots_dir, 'position_stats_no_covid_macd_mean_reversion.csv'), 'w', encoding='utf-8') as f:
        # write header
        f.write('stock_pair_label,strategy_string,num_days_long_A_short_B,num_days_long_B_short_A,num_days_no_position,'
                'average_holding_period\n')
        for strategy_string in ["StrategyB", "StrategyD"]:
            for stock_pair_label in pairs_portfolio_index_dict[strategy_string].keys():
                pairs_portfolio_index = pairs_portfolio_index_dict[strategy_string][stock_pair_label]
                pair_portfolio = master_portfolio.pair_portfolios[pairs_portfolio_index]
                position_over_time = np.array(pair_portfolio.position_over_time)
                num_days_in_position = {}
                num_days_in_position['long A short B'] = np.sum(position_over_time == 'long A short B')
                num_days_in_position['long B short A'] = np.sum(position_over_time == 'long B short A')
                num_days_in_position['no position'] = np.sum(position_over_time == 'no position')
                if strategy_string == "StrategyB":
                    output_strategy = "MACD"
                elif strategy_string == "StrategyD":
                    output_strategy = "Mean-reversion"
                # Calculate average length of time a position is held consecutively
                consecutive_days_in_position = {}
                consecutive_days_in_position['long A short B'] = []
                consecutive_days_in_position['long B short A'] = []
                consecutive_days_in_position['no position'] = []
                last_position = ''
                for next_position in position_over_time:
                    if next_position != last_position:
                        consecutive_days_in_position[next_position].append(1)
                    elif next_position == last_position:
                        consecutive_days_in_position[next_position][-1] += 1
                    last_position = next_position
                for position in ['long A short B', 'long B short A', 'no position']:
                    consecutive_days_in_position[position] = np.array(consecutive_days_in_position[position])
                average_holding_period = {}
                for position in ['long A short B', 'long B short A', 'no position']:
                    if len(consecutive_days_in_position[position]) == 0:
                        average_holding_period[position] = 0
                    else:
                        average_holding_period[position] = np.sum(consecutive_days_in_position[position]) / len(consecutive_days_in_position[position])
                average_holding_period_total = (average_holding_period['long A short B'] + average_holding_period['long B short A']) / 2
                # Write to CSV
                f.write(f'{stock_pair_label},{output_strategy},{num_days_in_position["long A short B"]},{num_days_in_position["long B short A"]},'
                        f'{num_days_in_position["no position"]},{average_holding_period_total}\n')
