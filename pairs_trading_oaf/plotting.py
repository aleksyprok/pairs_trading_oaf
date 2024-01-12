"""
Functions to plot trading data.
"""

import os
import matplotlib.pyplot as plt

def plot_portfolio_value_over_time(master_portfolio,
                                   plot_cash=True):
    """
    Plots the profit and loss of the portfolio over time for each pair
    in the master portfolio over the entire trading period.
    """
    current_dir = os.path.dirname(__file__)
    plots_dir = os.path.join(current_dir, '..', 'plots')
    os.makedirs(plots_dir, exist_ok=True)

    for pair_portfolio in master_portfolio.pair_portfolios:

        fig, ax = plt.subplots()
        fig_size = fig.get_size_inches()
        fig.set_size_inches(fig_size[0], fig_size[1])

        # Extract stock label text bettwen : and )
        stock_a_label = pair_portfolio.stock_pair_labels[0]
        stock_a_label = stock_a_label[stock_a_label.find(':')+1:stock_a_label.find(')')]
        stock_b_label = pair_portfolio.stock_pair_labels[1]
        stock_b_label = stock_b_label[stock_b_label.find(':')+1:stock_b_label.find(')')]

        ax.plot(pair_portfolio.dates_over_time, pair_portfolio.portfolio_value_over_time)
        ax.set_ylabel('Portfolio value [USD] (Position limit = $' +
                      f'{int(pair_portfolio.position_limit):d})')
        plt.xticks(rotation=45)
        ax.set_title('Portfolio value over time for\n' +
                     f'Stock pair: {stock_a_label}, {stock_b_label}\n' +
                     f'Strategy: {pair_portfolio.strategy.__class__.__name__}')
        fname = os.path.join(plots_dir, 'portfolio_value_over_time_' +
                             f'{pair_portfolio.strategy.__class__.__name__}' + '_' +
                             stock_a_label + '_' + stock_b_label + '.png')
        fig.savefig(fname, dpi=300, bbox_inches='tight')
        plt.close()

        if plot_cash:

            fig, ax = plt.subplots()
            ax.plot(pair_portfolio.dates_over_time, pair_portfolio.cash_over_time)
            ax.set_ylabel('Cash [USD] (Position limit = $' +
                        f'{int(pair_portfolio.position_limit):d})')
            plt.xticks(rotation=45)
            ax.set_title('Cash value over time for\n' +
                        f'Stock pair: {stock_a_label}, {stock_b_label}\n' +
                        f'Strategy: {pair_portfolio.strategy.__class__.__name__}')
            fname = os.path.join(plots_dir, 'cash_value_over_time_' +
                                f'{pair_portfolio.strategy.__class__.__name__}' + '_' +
                                stock_a_label + '_' + stock_b_label + '.png')
            fig.savefig(fname, dpi=300, bbox_inches='tight')
            plt.close()

    fig, ax = plt.subplots()

    ax.plot(master_portfolio.pair_portfolios[0].dates_over_time,
            master_portfolio.average_portfolio_value_over_time())
    ax.set_ylabel('Average portfolio value [USD] (Position limit = $' +
                  f'{int(master_portfolio.position_limit):d})')
    plt.xticks(rotation=45)
    ax.set_title('Average portfolio value over time')
    fname = os.path.join(plots_dir, 'average_portfolio_value_over_time.png')
    fig.savefig(fname, dpi=300, bbox_inches='tight')
    plt.close()

    if plot_cash:
        fig, ax = plt.subplots()
        ax.plot(master_portfolio.pair_portfolios[0].dates_over_time,
                master_portfolio.average_cash_over_time())
        ax.set_ylabel('Average cash [USD] (Position limit = $' +
                    f'{int(master_portfolio.position_limit):d})')
        plt.xticks(rotation=45)
        ax.set_title('Average cash over time')
        fname = os.path.join(plots_dir, 'average_cash_over_time.png')
        fig.savefig(fname, dpi=300, bbox_inches='tight')
        plt.close()
