"""
FISHER YATES SHUFFLE WITH NORMALIZED Tj

Compute the counters C0 and C1 for a given test on a series of sequences obtained via FY-shuffle from a starting one.
C0 is incremented if the result of the test T on a sequence is bigger than that on the following sequence; if the
results of the test are equal the second sequence is ignored. Each pair of sequences is considered as disjointed from
the following one.
Each counter is evaluated on a series of n_sequences sequences; n_iterations_c values of the counters are calculated.
"""

from architecture.utils.config import (
    n_sequences_stat,
    n_iterations_c_stat,
    test,
    distribution_test_index,
    p_value_stat,
)
from architecture.utils.useful_functions import execute_function, save_counters
from architecture.utils.shuffles import FY_shuffle
from architecture.utils.plot import counters_distribution_Tj
import time
from tqdm import tqdm
import logging


def counters_FY_TjNorm(S):
    counters_0 = []
    counters_1 = []
    for k in tqdm(range(n_iterations_c_stat)):
        Ti = []
        seq = FY_shuffle(S.copy())
        C0 = 0
        C1 = 0
        if distribution_test_index == 8 or distribution_test_index == 9:
            Ti.append(execute_function(test, seq, p_value_stat))
        else:
            Ti.append(execute_function(test, seq, None))
        j = 1
        while j < n_sequences_stat:
            seq = FY_shuffle(S.copy())
            if distribution_test_index == 8 or distribution_test_index == 9:
                t = execute_function(test, seq, p_value_stat)
            else:
                t = execute_function(test, seq, None)
            if t == Ti[j - 1]:
                continue
            else:
                Ti.append(t)
                j += 1

        for z in range(0, len(Ti) - 1, 2):
            if Ti[z] > Ti[z + 1]:
                C0 += 1
            if Ti[z] == Ti[z + 1]:
                C1 += 1

        counters_0.append(C0)
        counters_1.append(C1)

    logging.debug(f"FY_TjNorm counter_0: {counters_0}")
    logging.debug(f"FY_TjNorm counter_1: {counters_1}")

    return counters_0, counters_1


def FY_TjNorm(S):
    logging.debug("\nStatistical analysis FISHER YATES SHUFFLE WITH NORMALIZED Tj")
    f = (
        "/Users/olivia1/Desktop/random_power_entropy_val_new/architecture/results/counters_distribution"
        "/FYShuffleTjNorm/fyShuffleTjNorm_" + test + ".csv"
    )
    t = time.process_time()
    C0, C1 = counters_FY_TjNorm(S)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    save_counters(C0, C1, elapsed_time, "FY_shuffle", f)

    # Plot results
    counters_distribution_Tj(C0, n_sequences_stat, n_iterations_c_stat, "FY_TjNorm")
