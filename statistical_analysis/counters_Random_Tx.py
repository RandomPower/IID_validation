"""
RANDOM SAMPLING FROM FILE FOR REFERENCE VALUES

Compute the counters C0 and C1 for a given test on a series of random sequences read from file.
The given test is performed on the first sequence to obtain the reference value: C0 is incremented if the result of the
test T computed on a sequence is bigger than that it, C1 is incremented if they are equal.
Each counter is evaluated on a series of n_sequences sequences; n_iterations_c values of the counters are calculated.
"""

import logging
import os
import time

from tqdm import tqdm

import utils.config
import utils.plot
import utils.shuffles
import utils.useful_functions


def counters_Random_Tx(S):

    if utils.config.distribution_test_index == 8 or utils.config.distribution_test_index == 9:
        Tx = utils.useful_functions.execute_function(utils.config.test, S, utils.config.p_value_stat)
    else:
        Tx = utils.useful_functions.execute_function(utils.config.test, S, None)
    counters_0 = []
    counters_1 = []
    index = utils.config.n_symbols_stat / 2

    for i in tqdm(range(utils.config.n_iterations_c_stat)):
        C0 = 0
        C1 = 0
        S_shuffled = utils.shuffles.shuffle_from_file(
            index, utils.config.n_symbols_stat, utils.config.n_sequences_stat
        )
        Ti = []
        for k in S_shuffled:
            if utils.config.distribution_test_index == 8 or utils.config.distribution_test_index == 9:
                Ti.append(utils.useful_functions.execute_function(utils.config.test, k, utils.config.p_value_stat))
            else:
                Ti.append(utils.useful_functions.execute_function(utils.config.test, k, None))

        for z in range(len(Ti)):
            if Tx > Ti[z]:
                C0 += 1
            if Tx == Ti[z]:
                C1 += 1
        index += utils.config.n_sequences_stat * (utils.config.n_symbols_stat / 2)

        counters_0.append(C0)
        counters_1.append(C1)

    logging.debug("Random_Tx counter_0: %s", counters_0)
    logging.debug("Random_Tx counter_1: %s", counters_1)

    return counters_0, counters_1


def Random_Tx(S):
    logging.debug("\nStatistical analysis RANDOM SAMPLING FROM FILE FOR Tx VALUES")
    f = os.path.abspath(
        os.path.join(
            "results",
            "counters_distribution",
            "RandomTx",
            f"RandomTx_{utils.config.test}.csv",
        )
    )
    t = time.process_time()
    C0, C1 = counters_Random_Tx(S)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    utils.useful_functions.save_counters(C0, C1, elapsed_time, "Shuffle_from_file", f)

    # Plot results
    utils.plot.counters_distribution_Tx(
        C0, utils.config.n_sequences_stat, utils.config.n_iterations_c_stat, "Random_Tx"
    )
