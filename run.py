"""
This script runs the Monte Carlo simulation and generates the desired plots.

Required Input Files:
    settings.csv - Contains the constants to use in the Monte Carlo simulation.

Output Files:
    results.csv - Contains the results from the Monte Carlo simulation.
    simulation.png - Time evolution of the stock price.
"""

import os
import pandas as pd
from time import time
from heston import plot, simulate


# ***************************************************************************************
if __name__ == "__main__":

    # Delete the old output files
    # -----------------------------------------------------------------------------------
    for name in ['simulation.png', 'results.csv']:
        if os.path.isfile(name):
            os.remove(name)

    # Read the settings
    # -----------------------------------------------------------------------------------
    settings = pd.read_csv('settings.csv', squeeze=True, index_col='name')

    # Perform the simulation
    # -----------------------------------------------------------------------------------
    print('Starting the simulation.')
    start = time()
    simulation_results = simulate(settings)
    print("Simulation time: {:.1f} seconds.".format(time() - start))
    print("Number of time steps is {:.0f}.".format(settings['n']))
    print("Number of simulations is {:.0f}.".format(settings['m']))

    # Make some pretty plots
    # -----------------------------------------------------------------------------------
    plot(settings, simulation_results)
