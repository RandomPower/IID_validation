"""
RANDOM SAMPLING FROM FILE WITH Tj NORMALIZED

Compute the counters C0 and C1 for a given test on a series of random sequences read from file. C0 is incremented if
the result of the test T on a sequence is bigger than that on the following sequence; if the results of the test are
equal the second sequence is ignored. Each pair of sequences is considered as disjointed from the following one. Each
counter is evaluated on a series of n_sequences_stat sequences; n_iterations_c_stat values of the counters are
calculated.
"""

from architecture.utils.config import (
    n_symbols_stat,
    n_sequences_stat,
    n_iterations_c_stat,
    test,
    distribution_test_index,
    p_value_stat,
)
from architecture.utils.useful_functions import execute_function, save_counters
from architecture.utils.shuffles import shuffle_from_file_Norm
from architecture.utils.plot import counters_distribution_Tj
import time
import os
from tqdm import tqdm


def counters_FY_TjNorm(S):
    if distribution_test_index == 8 or distribution_test_index == 9:
        Tx = execute_function(test, S, p_value_stat)
    else:
        Tx = execute_function(test, S, None)

    counters_0 = []
    counters_1 = []
    index = 0

    for k in tqdm(range(n_iterations_c_stat)):
        C0 = 0
        C1 = 0
        s_sequences, Ti = shuffle_from_file_Norm(index, n_symbols_stat, n_sequences_stat, test)

        for z in range(0, len(Ti) - 1, 2):
            if Ti[z] > Ti[z + 1]:
                C0 += 1
            if Ti[z] == Ti[z + 1]:
                C1 += 1

        counters_0.append(C0)
        counters_1.append(C1)
        index += n_sequences_stat * n_symbols_stat / 2

    print(f"Random_TjNorm counter_0: {counters_0}")
    print(f"Random_TjNorm counter_1: {counters_1}")

    return counters_0, counters_1


def Random_TjNorm(S):
    print("\nStatistical analysis RANDOM SAMPLING FROM FILE WITH Tj NORMALIZED")
    f = os.path.abspath(
        os.path.join(
            "results",
            "counters_distribution",
            "RandomTjNorm",
            f"randomTjNorm_{test}.csv",
        )
    )
    t = time.process_time()
    C0, C1 = counters_FY_TjNorm(S)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    save_counters(C0, C1, elapsed_time, "Shuffle_from_file", f)

    # Plot results
    counters_distribution_Tj(C0, n_sequences_stat, n_iterations_c_stat, "Random_TjNorm")
