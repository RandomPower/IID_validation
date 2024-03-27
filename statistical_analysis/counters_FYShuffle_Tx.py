import logging
import os
import time

from tqdm import tqdm

import utils.config
import utils.plot
import utils.shuffles
import utils.useful_functions


def counters_FYShuffle_Tx(S):
    """Compute the counters C0 and C1 for a given test on a series of sequences obtained via FY-shuffle from a starting one.
    The given test is performed on the first sequence to obtain the reference value: 
    C0 is incremented if the result of the test T computed on a sequence is bigger than that it, C1 is incremented if they are equal.

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    list of int, list of int
        counter 0 and counter 1 lists of values
    """
    counters_0 = []
    counters_1 = []
    # Calculate reference statistics
    if utils.config.distribution_test_index == 8 or utils.config.distribution_test_index == 9:
        Tx = utils.useful_functions.execute_function(utils.config.test, S, utils.config.p_value_stat)
    else:
        Tx = utils.useful_functions.execute_function(utils.config.test, S, None)

    # S_shuffled will move by a P_pointer for every n_sequences
    for i in tqdm(range(utils.config.n_iterations_c_stat)):
        C0 = 0
        C1 = 0
        Ti = []
        for k in range(utils.config.n_sequences_stat):
            s_shuffled = utils.shuffles.FY_shuffle(S.copy())
            if utils.config.distribution_test_index == 8 or utils.config.distribution_test_index == 9:
                Ti.append(
                    utils.useful_functions.execute_function(utils.config.test, s_shuffled, utils.config.p_value_stat)
                )
            else:
                Ti.append(utils.useful_functions.execute_function(utils.config.test, s_shuffled, None))

        for z in range(len(Ti)):
            if Tx > Ti[z]:
                C0 += 1
            if Tx == Ti[z]:
                C1 += 1
        counters_0.append(C0)
        counters_1.append(C1)

    logging.debug("FY_Tx counter_0: %s", counters_0)
    logging.debug("FY_Tx counter_1: %s", counters_1)

    return counters_0, counters_1


def FY_Tx(S):
    """Calculates counter 0 and counter 1 list of values considering a series of sequences obtained via FY-shuffle from a starting one, 
    save the values in a file and plot the distribution

    Parameters
    ----------
    S : list of int
        sequence of sample values
    """
    logging.debug("Statistical analysis FISHER YATES SHUFFLE FOR Tx VALUES")
    f = os.path.abspath(
        os.path.join(
            "results",
            "counters_distribution",
            "FYShuffleTx",
            f"fyShuffleTx_{utils.config.test}.csv",
        )
    )
    t = time.process_time()
    C0, C1 = counters_FYShuffle_Tx(S)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    utils.useful_functions.save_counters(C0, C1, elapsed_time, "FY_shuffle", f)

    # Plot results
    utils.plot.counters_distribution_Tx(C0, utils.config.n_sequences_stat, utils.config.n_iterations_c_stat, "FY_Tx")
