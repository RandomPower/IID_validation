"""
RANDOM SAMPLING FROM FILE FOR REFERENCE VALUES

Compute the counters C0 and C1 for a given test on a series of random sequences read from file.
The given test is performed on the first sequence to obtain the reference value: C0 is incremented if the result of the test T
computed on a sequence is bigger than that it, C1 is incremented if they are equal.
Each counter is evaluated on a series of n_sequences sequences; n_iterations_c values of the counters are calculated.
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
from architecture.utils.shuffles import shuffle_from_file
from architecture.utils.plot import counters_distribution_Tx
import time
from tqdm import tqdm


def counters_Random_Tx(S):

    if distribution_test_index == 8 or distribution_test_index == 9:
        Tx = execute_function(test, S, p_value_stat)
    else:
        Tx = execute_function(test, S, None)
    counters_0 = []  # shape = (n_iterations_c x 1)
    counters_1 = []
    index = n_symbols_stat / 2

    for i in tqdm(range(n_iterations_c_stat)):
        C0 = 0
        C1 = 0
        S_shuffled = shuffle_from_file(index, n_symbols_stat, n_sequences_stat)
        Ti = []
        for k in S_shuffled:
            if distribution_test_index == 8 or distribution_test_index == 9:
                Ti.append(execute_function(test, k, p_value_stat))
            else:
                Ti.append(execute_function(test, k, None))

        for z in range(len(Ti)):
            if Tx > Ti[z]:
                C0 += 1
            if Tx == Ti[z]:
                C1 += 1
        index += n_sequences_stat * (n_symbols_stat / 2)

        counters_0.append(C0)
        counters_1.append(C1)

    print(f"Random_Tx counter_0: {counters_0}")
    print(f"Random_Tx counter_1: {counters_1}")

    return counters_0, counters_1


def Random_Tx(S):
    print("\nStatistical analysis RANDOM SAMPLING FROM FILE FOR Tx VALUES")
    f = (
        "./results/counters_distribution/RandomTx/randomTx_" + test + ".csv"
    )
    t = time.process_time()
    C0, C1 = counters_Random_Tx(S)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    save_counters(C0, C1, elapsed_time, "Shuffle_from_file", f)

    # Plot results
    counters_distribution_Tx(C0, n_sequences_stat, n_iterations_c_stat, "Random_Tx")
