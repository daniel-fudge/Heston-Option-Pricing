"""
This script runs the Monte Carlo simulation and generates the desired plots.

Required Input Files:
    settings.csv - Contains the constants to use in the Monte Carlo simulation.

Output Files:
    results.csv - Contains the results from the Monte Carlo simulation.
    simulation.png - Time evolution of the stock price.
"""

import numpy as np
import os
from scipy import stats
from time import time


# ***************************************************************************************
def simulate():
    """ Performs the Monte Carlo simulation.

    Output Files:
        simulation.png - Time evolution of the stock price.

    Returns:
        np.array:  [m, n+1] The m simulation results with n time steps.
    """

    print('Starting the simulation.')
    start = time()

    # Set the constants
    # -----------------------------------------------------------------------------------
    r = 0.0319
    s_o = k = 2.0
    t_max = 1.0
    v_o = 0.010201
    sigma = 0.61
    theta = 0.019
    kappa = 6.21
    rho_choice = np.array([-0.5, -0.7, -0.9])
    rho_probability = np.array([0.25, 0.5, 0.25])
    n = 400
    m = n * n

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
    expected_price = s[:, -1].mean()
    price_std = s[:, -1].std()
    price_error = price_std / np.sqrt(m)
    bins = np.arange(s[:, -1].min(), s[:, -1].max() + 0.02, 0.02)
    price_mode = bins[np.histogram(s[:, -1], bins=bins)[0].argmax()] + 0.01

    payoff = np.clip(s[:, -1] - k, a_min=0, a_max=None)
    expected_payoff = payoff.mean()
    payoff_std = payoff.std()
    payoff_error = payoff_std / np.sqrt(m)
    bins = np.arange(payoff.min(), payoff.max() + 0.02, 0.02)
    payoff_mode = bins[np.histogram(payoff, bins=bins)[0].argmax()] + 0.01

    c = expected_payoff * np.exp(-r * t_max)

    print("Expected fuel price: ${:.4f} +/- ${:.4f}.".format(expected_price, price_error))
    print("Expected payoff:     ${:.4f} +/- ${:.4f}.".format(expected_payoff, payoff_error))
    print(" => Option price:    ${:.4f}.".format(c))
    print("Total price to cover 2 Million Gallons is ${:,.0f}.\n".format(c * 2000000))

    print("Price Mean, Mode, STD:  ${:.4f}, ${:.4f}, ${:.4f}.".format(expected_price, price_mode, price_std))
    print("Payoff Mean, Mode, STD: ${:.4f}, ${:.4f}, ${:.4f}.\n".format(expected_payoff, payoff_mode, payoff_std))

    print("Simulation time: {:.1f} seconds.".format(time() - start))
    print("Number of time steps:  {:.0f}.".format(n))
    print("Number of simulations: {:,.0f}.".format(m))
    print("Total number samples:  {:,.0f}.".format(m * n))

    # Make pretty plots
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
    t = np.linspace(0, t_max, num=n + 1)
    ns = 40
    for i in range(ns):
        ax_lines.plot(t, s[i, :], lw=1.0)
    ax_lines.set(xlabel='Years', ylabel='Price of Fuel (St)',
                 title='Fuel Price Simulations ({} of {:,.0f} plotted)'.format(ns, m))
    ax_lines.set_xlim((0, 1))
    ax_lines.set_ylim((1.4, 2.6))

    # Add mean value to line plots
    ax_lines.plot([0.0, 1.0], [expected_price, expected_price], lw='2', ls="--")

    # Make the histogram for the final stock prices S_T
    bins = np.arange(1.4, 3, .04)
    ax_histogram.hist(s[:, -1], bins=bins, orientation='horizontal')
    ax_histogram.set_ylim(ax_lines.get_ylim())
    ax_histogram.xaxis.set_major_formatter(NullFormatter())
    ax_histogram.yaxis.set_major_formatter(NullFormatter())
    plt.savefig("simulation.png")

    # Make the histogram for the Payoffs
    plt.figure()
    plt.hist(payoff, bins=np.arange(0.0, 0.62, 0.02), density=True)
    plt.title("Simulated Option Payoffs")
    plt.xlabel("Option Payoff")
    plt.ylabel("Probability")
    plt.savefig("payoffs.png")


# ***************************************************************************************
if __name__ == "__main__":

    # Delete the old output files
    # -----------------------------------------------------------------------------------
    for name in ['simulation.png', 'results.csv']:
        if os.path.isfile(name):
            os.remove(name)

    # Run the simulation
    # -----------------------------------------------------------------------------------
    simulate()
