from utils.config import (
    n_symbols_stat,
    n_sequences_stat,
    n_iterations_c_stat,
    test,
)
from utils.useful_functions import save_counters
from utils.shuffles import shuffle_from_file_Norm
from utils.plot import counters_distribution_Tj
import time
import os
from tqdm import tqdm
import logging


def counters_random_TjNorm():
    """Compute the counters C0 and C1 for a given test on a series of random sequences read from file. 
    C0 is incremented if the result of the test T on a sequence is bigger than that on the following sequence; 
    if the results of the test are equal the second sequence is ignored. 
    Each pair of sequences is considered as disjointed from the following one. 

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

    logging.debug("Random_TjNorm counter_0: %s", counters_0)
    logging.debug("Random_TjNorm counter_1: %s", counters_1)

    return counters_0, counters_1


def Random_TjNorm(S):
    """Calculates counter 0 and counter 1 list of values considering a series of random sequences read from file, 
    save the values in a file and plot the distribution

    Parameters
    ----------
    S : list of int
        sequence of sample values
    """
    logging.debug("\nStatistical analysis RANDOM SAMPLING FROM FILE WITH Tj NORMALIZED")
    f = os.path.abspath(
        os.path.join(
            "results",
            "counters_distribution",
            "RandomTjNorm",
            f"randomTjNorm_{test}.csv",
        )
    )
    t = time.process_time()
    C0, C1 = counters_random_TjNorm()
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    save_counters(C0, C1, elapsed_time, "Shuffle_from_file", f)

    # Plot results
    counters_distribution_Tj(C0, n_sequences_stat, n_iterations_c_stat, "Random_TjNorm")
