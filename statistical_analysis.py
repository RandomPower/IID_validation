import logging
import os
import pathlib
import time

from tqdm import tqdm

import permutation_tests
import utils.config
import utils.plot
import utils.useful_functions

# Configure per-module logger
logger = logging.getLogger(f"IID_validation.{pathlib.Path(__file__).stem}")


def get_C0_C1_TjNorm(Ti):
    """Compute the counters C0 and C1 for a given reference list of values Ti with the TjNorm method: the elements of Ti
    are considered in non-overlapping pairs: if the first element of the couple is bigger that the following one, C0 is
    incremented; if they are equal C1 is.

    Parameters
    ----------
    Ti : list of float
        list of values to compare

    Returns
    -------
    int, int
        counter 0 and counter 1
    """
    C0 = 0
    C1 = 0
    for z in range(0, len(Ti) - 1, 2):
        if Ti[z] > Ti[z + 1]:
            C0 += 1
        if Ti[z] == Ti[z + 1]:
            C1 += 1

    return C0, C1


def calculate_counters_Tx(conf: utils.config.Config, S: list[int], test: int) -> tuple[list[int], list[int]]:
    """Compute the counters C0 and C1 for a given test on a series of sequences obtained via FY-shuffle from a starting
    one. The given test is performed on the first sequence to obtain the reference value:
    C0 is incremented if the result of the test T computed on a sequence is bigger than that it,
    C1 is incremented if they are equal.

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    S : list of int
        sequence of sample values
    test: int
        index of the test

    Returns
    -------
    list of int, list of int
        counter 0 and counter 1 lists of values
    """
    counters_0 = []
    counters_1 = []
    # Calculate reference statistics
    if test in [8, 9]:
        Tx = permutation_tests.tests[test].run(S, conf.stat.p)
    else:
        Tx = permutation_tests.tests[test].run(S)

    # S_shuffled will move by a P_pointer for every n_sequences
    for i in tqdm(range(conf.stat.n_iterations)):
        Ti = []
        for k in range(conf.stat.n_sequences):
            s_shuffled = permutation_tests.FY_shuffle(S.copy())
            if test in [8, 9]:
                Ti.append(permutation_tests.tests[test].run(s_shuffled, conf.stat.p))
            else:
                Ti.append(permutation_tests.tests[test].run(s_shuffled))

        C0, C1 = permutation_tests.get_C0_C1_Tx(Tx, Ti)
        counters_0.append(C0)
        counters_1.append(C1)

    logger.debug("Tx counter_0: %s", counters_0)
    logger.debug("Tx counter_1: %s", counters_1)

    return counters_0, counters_1


def counters_Tx(conf: utils.config.Config, S: list[int], test: int):
    """Calculates counter 0 and counter 1 list of values considering a series of sequences obtained via FY-shuffle from
    a starting one, save the values in a file and plot the distribution

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    S : list of int
        sequence of sample values
    test: int
        index of the test
    """
    logger.debug("Statistical analysis FISHER YATES SHUFFLE FOR Tx VALUES")
    # Define and create the directory
    directory_path = os.path.join(
        "statistical_analysis",
        "countersTx_distribution",
    )
    os.makedirs(directory_path, exist_ok=True)

    f = os.path.join(directory_path, f"countersTx_{permutation_tests.tests[test].name}.csv")
    t = time.process_time()
    C0, C1 = calculate_counters_Tx(conf, S, test)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    utils.useful_functions.save_counters(conf, C0, C1, elapsed_time, f, test)

    # Plot results
    utils.plot.counters_distribution_Tx(
        C0,
        conf.stat.n_sequences,
        conf.stat.n_iterations,
        test,
        "countersTx",
        directory_path,
    )


def calculate_counters_TjNorm(conf: utils.config.Config, S: list[int], test: int) -> tuple[list[int], list[int]]:
    """Compute the counters C0 and C1 for a given test on a series of sequences obtained via FY-shuffle from a starting
    one. C0 is incremented if the result of the test T on a sequence is bigger than that on the following sequence; if
    the results of the test are equal the second sequence is ignored.
    Each pair of sequences is considered as disjointed from the following one.


    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    S : list of int
        sequence of sample values
    test: int
        index of the test

    Returns
    -------
    list of int, list of int
        counter 0 and counter 1 lists of values
    """
    counters_0 = []
    counters_1 = []
    for k in tqdm(range(conf.stat.n_iterations)):
        Ti = []
        seq = permutation_tests.FY_shuffle(S.copy())
        if test in [8, 9]:
            Ti.append(permutation_tests.tests[test].run(seq, conf.stat.p))
        else:
            Ti.append(permutation_tests.tests[test].run(seq))
        j = 1
        while j < conf.stat.n_sequences:
            seq = permutation_tests.FY_shuffle(S.copy())
            if test in [8, 9]:
                t = permutation_tests.tests[test].run(seq, conf.stat.p)
            else:
                t = permutation_tests.tests[test].run(seq)
            if t == Ti[j - 1]:
                continue
            else:
                Ti.append(t)
                j += 1

        C0, C1 = get_C0_C1_TjNorm(Ti)
        counters_0.append(C0)
        counters_1.append(C1)

    logger.debug("TjNorm counter_0: %s", counters_0)
    logger.debug("TjNorm counter_1: %s", counters_1)

    return counters_0, counters_1


def counters_TjNorm(conf: utils.config.Config, S: list[int], test: int):
    """Calculates counter 0 and counter 1 list of values considering a series of sequences obtained via FY-shuffle from
    a starting one, save the values in a file and plot the distribution

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    S : list of int
        sequence of sample values
    test: int
        index of the test
    """
    logger.debug("\nStatistical analysis FISHER YATES SHUFFLE WITH NORMALIZED Tj")
    # Define and create the directory
    directory_path = os.path.join(
        "statistical_analysis",
        "countersTjNorm_distribution",
    )
    os.makedirs(directory_path, exist_ok=True)

    f = os.path.join(
        directory_path,
        f"countersTjNorm_{permutation_tests.tests[test].name}.csv",
    )
    t = time.process_time()
    C0, C1 = calculate_counters_TjNorm(conf, S, test)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    utils.useful_functions.save_counters(conf, C0, C1, elapsed_time, f, test)

    # Plot results
    utils.plot.counters_distribution_Tj(
        C0,
        conf.stat.n_sequences,
        conf.stat.n_iterations,
        test,
        "countersTjNorm",
        directory_path,
    )
