import pandas as pd 

import seaborn as sns
import matplotlib.pyplot as plt


def plot_rate_fact(data, machine_type, date, fig_path=None, y_value="rate_fact"):
    sns.set_theme(style="whitegrid")
    sns.set(rc={'figure.figsize':(21,8)})
    sns.set(style='white')

    df = data[(data.machine_type == machine_type) & (data.date > date)]
    ax = sns.lineplot(data=df, x='date', y=y_value)

    ax.yaxis.tick_right()
    
    ax2 = ax.twinx()
    sns.lineplot(data=df, x='date', y='ratio', ax=ax2, color='#EF9A9A')
    ax2.set(xlabel='', ylabel='Плотность расходов на метр в сутки')

    ax.set_title('Фактический расход топлива y серии {}'.format(machine_type), fontsize=15)
    ax.set(xlabel='', ylabel='Валовый расход в сутки')
    
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(10))

    ax.grid(True)

    file_name = '{0}_{1}.png'.format(machine_type, date)

    if fig_path:
        plt.savefig(fig_path.format(file_name))