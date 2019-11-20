"""
This module contains the Monte Carlo simulation and plotting functions.
"""

import numpy as np
import pandas as pd


# ***************************************************************************************
def simulate(settings):
    """ Performs the Monte Carlo simulation.

    Required Input Files:
        settings.csv - Contains the constants to use in the Monte Carlo simulation.

    Output Files:
        simulation.png - Time evolution of the stock price.

    Returns:
        np.array:  [m, n+1] The m simulation results with n time steps.
    """

    # Read settings file
    # -----------------------------------------------------------------------------------
    r = settings['r']
    k = settings['K']
    s_o = settings['So']
    t_max = settings['T']
    v_o = settings['Vo']
    sigma = settings['sigma']
    theta = settings['theta']
    kappa = settings['kappa']
    n_rho = int(settings['n_rho'])
    rho_choice = np.array([settings['rho_{}'.format(i)] for i in range(n_rho)])
    rho_probability = np.array([settings['rho_probability_{}'.format(i)] for i in range(n_rho)])
    m = int(settings['m'])
    n = int(settings['n'])

    # Create random parameters
    # -----------------------------------------------------------------------------------
    dt = t_max / n
    dw_v = np.random.normal(size=(m, n)) * np.sqrt(dt)
    dw_i = np.random.normal(size=(m, n)) * np.sqrt(dt)
    rho = np.random.choice(rho_choice, size=(m, 1), p=rho_probability)
    dw_s = rho * dw_v + np.sqrt(1.0 - rho ** 2) * dw_i

    # Perform time evolution (only saving all s values for plotting)
    #    Could also speed this up by using log-returns and coefficients for repeated
    #    multiplication but this is easier to read.
    # -----------------------------------------------------------------------------------
    s = np.empty((m, n + 1))
    s[:, 0] = s_o
    v = np.ones(m) * v_o
    for t in range(n):
        dv = kappa * (theta - v) * dt + sigma * np.sqrt(v) * dw_v[:, t]
        ds = r * s[:, t] * dt + np.sqrt(v) * s[:, t] * dw_s[:, t]
        v = np.clip(v + dv, a_min=0.0, a_max=None)
        s[:, t + 1] = s[:, t] + ds

    # Calculate expected call option payoff and therefore option price
    # -----------------------------------------------------------------------------------
    expected_payoff = np.clip(s[:, -1] - k, a_min=0, a_max=None).mean()
    c = expected_payoff * np.exp(-r * t_max)
    print("Expected payoff is ${:.2f}.".format(expected_payoff))
    print("Call option price is ${:.2f}.".format(c))

    return s


# ***************************************************************************************
def plot(settings, s=None):
    """ Generates the required plots from the simulation.

    Output Files:
        simulation.png - Time evolution of the stock price.

    Args:
        settings (pd.DataFrame):  Contents of settings.csv.
        s (np.array):  The stock price histories.
    """

    # Make pretty plot
    # -----------------------------------------------------------------------------------
    import matplotlib.pyplot as plt
    from matplotlib.ticker import NullFormatter
    import seaborn as sns
    sns.set(style="darkgrid")

    # Setup figure
    plt.figure()
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.8
    left_h = left + width + 0.02
    rect_lines = [left, bottom, width, height]
    rect_histogram = [left_h, bottom, 0.2, height]
    # noinspection PyTypeChecker
    ax_lines = plt.axes(rect_lines)
    # noinspection PyTypeChecker
    ax_histogram = plt.axes(rect_histogram)

    # Make the line plots
    t = np.linspace(0, settings['T'], num=int(settings['n']) + 1)
    for i in range(20):
        ax_lines.plot(t, s[i, :], lw=1.0)
    ax_lines.set(xlabel='Years', ylabel='Stock Price (St)',
                 title='Stock Price Simulations (20 of {} plotted)'.format(int(settings['m'])))
    ax_lines.set_xlim((0, 1))
    ax_lines.set_ylim((70, 130))

    # Make the histogram for the final stock prices S_T
    bins = np.arange(70, 132, 2)
    ax_histogram.hist(s[:, -1], bins=bins, orientation='horizontal')
    ax_histogram.set_ylim(ax_lines.get_ylim())
    ax_histogram.xaxis.set_major_formatter(NullFormatter())
    ax_histogram.yaxis.set_major_formatter(NullFormatter())
    plt.savefig("simulation.png")
