from utils.config import (
    n_symbols_stat,
    n_sequences_stat,
    n_iterations_c_stat,
    test,
    distribution_test_index,
    p_value_stat,
)
from utils.useful_functions import execute_function, save_counters
from utils.shuffles import FY_shuffle
from utils.plot import counters_distribution_Tj
import time
import os
from tqdm import tqdm


def counters_FY_TjNorm(S):
    """Compute the counters C0 and C1 for a given test on a series of sequences obtained via FY-shuffle from a starting one.
    C0 is incremented if the result of the test T on a sequence is bigger than that on the following sequence; if the results of the
    test are equal the second sequence is ignored. Each pair of sequences is considered as disjointed from the following one.


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

    print(f"FY_TjNorm counter_0: {counters_0}")
    print(f"FY_TjNorm counter_1: {counters_1}")

    return counters_0, counters_1


def FY_TjNorm(S):
    """Calculates counter 0 and counter 1 list of values considering a series of sequences obtained via FY-shuffle from a starting one, 
    save the values in a file and plot the distribution

    Parameters
    ----------
    S : list of int
        sequence of sample values
    """
    print("\nStatistical analysis FISHER YATES SHUFFLE WITH NORMALIZED Tj")
    f = os.path.abspath(
        os.path.join(
            "results",
            "counters_distribution",
            "FYShuffleTjNorm",
            f"fyShuffleTjNorm_{test}.csv",
        )
    )
    t = time.process_time()
    C0, C1 = counters_FY_TjNorm(S)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    save_counters(C0, C1, elapsed_time, "FY_shuffle", f)

    # Plot results
    counters_distribution_Tj(C0, n_sequences_stat, n_iterations_c_stat, "FY_TjNorm")
