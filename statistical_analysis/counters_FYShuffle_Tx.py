"""
FISHER YATES SHUFFLE FOR REFERENCE VALUES

Compute the counters C0 and C1 for a given test on a series of sequences obtained via FY-shuffle from a starting one.
The given test is performed on the first sequence to obtain the reference value: C0 is incremented if the result of the
test T computed on a sequence is bigger than that it, C1 is incremented if they are equal.
Each counter is evaluated on a series of n_sequences sequences; n_iterations_c values of the counters are calculated.
"""

from utils.config import (
    n_sequences_stat,
    n_iterations_c_stat,
    test,
    distribution_test_index,
    p_value_stat,
)
from utils.useful_functions import execute_function, save_counters
from utils.shuffles import FY_shuffle
from utils.plot import counters_distribution_Tx
import time
import os
from tqdm import tqdm
import logging


def counters_FYShuffle_Tx(S):
    counters_0 = []
    counters_1 = []
    # Calculate reference statistics
    if distribution_test_index == 8 or distribution_test_index == 9:
        Tx = execute_function(test, S, p_value_stat)
    else:
        Tx = execute_function(test, S, None)

    # S_shuffled will move by a P_pointer for every n_sequences
    for i in tqdm(range(n_iterations_c_stat)):
        C0 = 0
        C1 = 0
        Ti = []
        for k in range(n_sequences_stat):
            s_shuffled = FY_shuffle(S.copy())
            if distribution_test_index == 8 or distribution_test_index == 9:
                Ti.append(execute_function(test, s_shuffled, p_value_stat))
            else:
                Ti.append(execute_function(test, s_shuffled, None))

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
    logging.debug("Statistical analysis FISHER YATES SHUFFLE FOR Tx VALUES")
    f = os.path.abspath(
        os.path.join(
            "results",
            "counters_distribution",
            "FYShuffleTx",
            f"fyShuffleTx_{test}.csv",
        )
    )
    t = time.process_time()
    C0, C1 = counters_FYShuffle_Tx(S)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    save_counters(C0, C1, elapsed_time, "FY_shuffle", f)

    # Plot results
    counters_distribution_Tx(C0, n_sequences_stat, n_iterations_c_stat, "FY_Tx")
