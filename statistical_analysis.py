import logging
import os
import pathlib
import time

import pandas as pd
from tqdm import tqdm

import permutation_tests
import utils.config
import utils.plot
import utils.shuffles
import utils.useful_functions

# Configure per-module logger
logger = logging.getLogger(f"IID_validation.{pathlib.Path(__file__).stem}")


def counters_FYShuffle_Tx(conf: utils.config.Config, S):
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

    Returns
    -------
    list of int, list of int
        counter 0 and counter 1 lists of values
    """
    counters_0 = []
    counters_1 = []
    test = conf.stat.distribution_test_index
    # Calculate reference statistics
    if test in [8, 9]:
        Tx = permutation_tests.tests[test].run(S, conf.stat.p_value)
    else:
        Tx = permutation_tests.tests[test].run(S)

    # S_shuffled will move by a P_pointer for every n_sequences
    for i in tqdm(range(conf.stat.n_iterations_c)):
        C0 = 0
        C1 = 0
        Ti = []
        for k in range(conf.stat.n_sequences):
            s_shuffled = permutation_tests.FY_shuffle(S.copy())
            if test in [8, 9]:
                Ti.append(permutation_tests.tests[test].run(s_shuffled, conf.stat.p_value))
            else:
                Ti.append(permutation_tests.tests[test].run(s_shuffled))

        for z in range(len(Ti)):
            if Tx > Ti[z]:
                C0 += 1
            if Tx == Ti[z]:
                C1 += 1
        counters_0.append(C0)
        counters_1.append(C1)

    logger.debug("FY_Tx counter_0: %s", counters_0)
    logger.debug("FY_Tx counter_1: %s", counters_1)

    return counters_0, counters_1


def FY_Tx(conf: utils.config.Config, S):
    """Calculates counter 0 and counter 1 list of values considering a series of sequences obtained via FY-shuffle from
    a starting one, save the values in a file and plot the distribution

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    S : list of int
        sequence of sample values
    """
    logger.debug("Statistical analysis FISHER YATES SHUFFLE FOR Tx VALUES")
    # Define and create the directory
    directory_path = os.path.join(
        "statistical_analysis",
        "FYShuffleTx",
    )
    os.makedirs(directory_path, exist_ok=True)

    f = os.path.join(
        directory_path, f"fyShuffleTx_{permutation_tests.tests[conf.stat.distribution_test_index].name}.csv"
    )
    t = time.process_time()
    C0, C1 = counters_FYShuffle_Tx(conf, S)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    utils.useful_functions.save_counters(conf, C0, C1, elapsed_time, "FY_shuffle", f)

    # Plot results
    utils.plot.counters_distribution_Tx(
        C0,
        conf.stat.n_sequences,
        conf.stat.n_iterations_c,
        conf.stat.distribution_test_index,
        "FY_Tx",
        directory_path,
    )


def counters_Random_Tx(conf: utils.config.Config, S):
    """Compute the counters C0 and C1 for a given test on a series of random sequences read from file.
    The given test is performed on the first sequence to obtain the reference value: C0 is incremented if the result
    of the test T computed on a sequence is bigger than that it, C1 is incremented if they are equal.

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    S : list of int
        sequence of sample values

    Returns
    -------
    list of int, list of int
        counter 0 and counter 1 lists of values
    """
    test = conf.stat.distribution_test_index
    if test in [8, 9]:
        Tx = permutation_tests.tests[test].run(S, conf.stat.p_value)
    else:
        Tx = permutation_tests.tests[test].run(S)
    counters_0 = []
    counters_1 = []
    index = conf.stat.n_symbols / 2

    for i in tqdm(range(conf.stat.n_iterations_c)):
        C0 = 0
        C1 = 0
        S_shuffled = utils.shuffles.shuffle_from_file(
            conf.input_file, index, conf.stat.n_symbols, conf.stat.n_sequences
        )
        Ti = []
        for k in S_shuffled:
            if test in [8, 9]:
                Ti.append(permutation_tests.tests[test].run(k, conf.stat.p_value))
            else:
                Ti.append(permutation_tests.tests[test].run(k))

        for z in range(len(Ti)):
            if Tx > Ti[z]:
                C0 += 1
            if Tx == Ti[z]:
                C1 += 1
        index += conf.stat.n_sequences * (conf.stat.n_symbols / 2)

        counters_0.append(C0)
        counters_1.append(C1)

    logger.debug("Random_Tx counter_0: %s", counters_0)
    logger.debug("Random_Tx counter_1: %s", counters_1)

    return counters_0, counters_1


def Random_Tx(conf: utils.config.Config, S):
    """Calculates counter 0 and counter 1 list of values considering a series of random sequences read from file,
    save the values in a file and plot the distribution

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    S : list of int
        sequence of sample values
    """
    logger.debug("\nStatistical analysis RANDOM SAMPLING FROM FILE FOR Tx VALUES")
    # Define and create the directory
    directory_path = os.path.join(
        "statistical_analysis",
        "RandomTx",
    )
    os.makedirs(directory_path, exist_ok=True)

    f = os.path.join(
        directory_path,
        f"RandomTx_{permutation_tests.tests[conf.stat.distribution_test_index].name}.csv",
    )
    t = time.process_time()
    C0, C1 = counters_Random_Tx(conf, S)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    utils.useful_functions.save_counters(conf, C0, C1, elapsed_time, "Shuffle_from_file", f)

    # Plot results
    utils.plot.counters_distribution_Tx(
        C0,
        conf.stat.n_sequences,
        conf.stat.n_iterations_c,
        conf.stat.distribution_test_index,
        "Random_Tx",
        directory_path,
    )


def counters_FY_TjNorm(conf: utils.config.Config, S):
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

    Returns
    -------
    list of int, list of int
        counter 0 and counter 1 lists of values
    """
    counters_0 = []
    counters_1 = []
    test = conf.stat.distribution_test_index
    for k in tqdm(range(conf.stat.n_iterations_c)):
        Ti = []
        seq = permutation_tests.FY_shuffle(S.copy())
        C0 = 0
        C1 = 0
        if test in [8, 9]:
            Ti.append(permutation_tests.tests[test].run(seq, conf.stat.p_value))
        else:
            Ti.append(permutation_tests.tests[test].run(seq))
        j = 1
        while j < conf.stat.n_sequences:
            seq = permutation_tests.FY_shuffle(S.copy())
            if test in [8, 9]:
                t = permutation_tests.tests[test].run(seq, conf.stat.p_value)
            else:
                t = permutation_tests.tests[test].run(seq)
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

    logger.debug("FY_TjNorm counter_0: %s", counters_0)
    logger.debug("FY_TjNorm counter_1: %s", counters_1)

    return counters_0, counters_1


def FY_TjNorm(conf: utils.config.Config, S):
    """Calculates counter 0 and counter 1 list of values considering a series of sequences obtained via FY-shuffle from
    a starting one, save the values in a file and plot the distribution

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    S : list of int
        sequence of sample values
    """
    logger.debug("\nStatistical analysis FISHER YATES SHUFFLE WITH NORMALIZED Tj")
    distribution_test_index = conf.stat.distribution_test_index
    # Define and create the directory
    directory_path = os.path.join(
        "statistical_analysis",
        "FYShuffleTjNorm",
    )
    os.makedirs(directory_path, exist_ok=True)

    f = os.path.join(
        directory_path,
        f"fyShuffleTjNorm_{permutation_tests.tests[distribution_test_index].name}.csv",
    )
    t = time.process_time()
    C0, C1 = counters_FY_TjNorm(conf, S)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    utils.useful_functions.save_counters(conf, C0, C1, elapsed_time, "FY_shuffle", f)

    # Plot results
    utils.plot.counters_distribution_Tj(
        C0,
        conf.stat.n_sequences,
        conf.stat.n_iterations_c,
        conf.stat.distribution_test_index,
        "FY_TjNorm",
        directory_path,
    )


def counters_random_TjNorm(conf: utils.config.Config):
    """Compute the counters C0 and C1 for a given test on a series of random sequences read from file.
    C0 is incremented if the result of the test T on a sequence is bigger than that on the following sequence;
    if the results of the test are equal the second sequence is ignored.
    Each pair of sequences is considered as disjointed from the following one.

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters

    Returns
    -------
    list of int, list of int
        counter 0 and counter 1 lists of values
    """
    counters_0 = []
    counters_1 = []
    index = 0

    for k in tqdm(range(conf.stat.n_iterations_c)):
        C0 = 0
        C1 = 0
        s_sequences, Ti = utils.shuffles.shuffle_from_file_Norm(
            conf.input_file,
            index,
            conf.stat.n_symbols,
            conf.stat.n_sequences,
            conf.stat.distribution_test_index,
            conf,
        )

        for z in range(0, len(Ti) - 1, 2):
            if Ti[z] > Ti[z + 1]:
                C0 += 1
            if Ti[z] == Ti[z + 1]:
                C1 += 1

        counters_0.append(C0)
        counters_1.append(C1)
        index += conf.stat.n_sequences * conf.stat.n_symbols / 2

    logger.debug("Random_TjNorm counter_0: %s", counters_0)
    logger.debug("Random_TjNorm counter_1: %s", counters_1)

    return counters_0, counters_1


def Random_TjNorm(conf: utils.config.Config, S):
    """Calculates counter 0 and counter 1 list of values considering a series of random sequences read from file,
    save the values in a file and plot the distribution

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    S : list of int
        sequence of sample values
    """
    logger.debug("\nStatistical analysis RANDOM SAMPLING FROM FILE WITH Tj NORMALIZED")
    # Define and create the directory
    directory_path = os.path.join(
        "statistical_analysis",
        "RandomTjNorm",
    )
    os.makedirs(directory_path, exist_ok=True)

    f = os.path.join(
        directory_path,
        f"randomTjNorm_{permutation_tests.tests[conf.stat.distribution_test_index].name}.csv",
    )
    t = time.process_time()
    C0, C1 = counters_random_TjNorm(conf)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    utils.useful_functions.save_counters(conf, C0, C1, elapsed_time, "Shuffle_from_file", f)

    # Plot results
    utils.plot.counters_distribution_Tj(
        C0,
        conf.stat.n_sequences,
        conf.stat.n_iterations_c,
        conf.stat.distribution_test_index,
        "Random_TjNorm",
        directory_path,
    )


def get_data(ref_numbers, Tj_norm):
    """Reads the files corresponding to the reference test numbers and returns the counters values

    Parameters
    ----------
    ref_numbers : list of int
        tests to compare
    Tj_norm : boolean
        Tj norm / Tx

    Returns
    -------
    list of lists of int, list of lists of int
        counters values
    """
    # Construct the filenames based on reference numbers
    C0_fy = []
    C0_random = []
    for ref in ref_numbers:
        if Tj_norm:
            fy = os.path.join(
                "statistical_analysis",
                "FYShuffleTjNorm",
                f"fyShuffleTjNorm_{permutation_tests.tests[ref].name}.csv",
            )
            rand = os.path.join(
                "statistical_analysis",
                "RandomTjNorm",
                f"randomTjNorm_{permutation_tests.tests[ref].name}.csv",
            )
        else:
            fy = os.path.join(
                "statistical_analysis",
                "FYShuffleTx",
                f"fyShuffleTx_{permutation_tests.tests[ref].name}.csv",
            )
            rand = os.path.join(
                "statistical_analysis",
                "RandomTx",
                f"randomTx_{permutation_tests.tests[ref].name}.csv",
            )
        if not os.path.exists(fy):
            logger.error("Results file for test number %s does not exist: %s", ref, fy)
            raise ValueError(f"Results file for test number {ref} does not exist: {fy}")
        if not os.path.exists(rand):
            logger.error("Results file for test number %s does not exist: %s", ref, rand)
            raise ValueError(f"Results file for test number {ref} does not exist: {rand}")

        try:
            data1 = pd.read_csv(fy)
            data2 = pd.read_csv(rand)
            sixth_feature1 = data1.iloc[:, 5]
            sixth_feature2 = data2.iloc[:, 5]
            last_entry1 = sixth_feature1.iloc[-1]
            last_entry2 = sixth_feature2.iloc[-1]
            C0_fy.append(eval(last_entry1))
            C0_random.append(eval(last_entry2))
        except Exception as e:
            logger.error("Reading or processing files for test %s not successful: %s", permutation_tests.tests[ref], e)
            raise e
    return C0_fy, C0_random


def comparison_scatterplot(conf: utils.config.Config):
    """Plots the comparison scatterplot between FY_shuffle counters and reading from file for the specified tests.
    The counters values are read from csv files.

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    """
    test_indexes = conf.stat.ref_numbers
    test_names = [permutation_tests.tests[i].name for i in test_indexes]

    Cfy, Crand = get_data(test_indexes, False)
    Cfy_tjNorm, Crand_TjNorm = get_data(test_indexes, True)

    # Define directory where to save the plot
    directory_path = os.path.join("statistical_analysis", "comparison_FYvsRandom")

    # Ensure the directory exists
    os.makedirs(directory_path, exist_ok=True)

    # Plot the results
    utils.plot.scatterplot_RvsFY(test_names, Crand, Cfy, directory_path)
    utils.plot.scatterplot_RvsFY_TjNorm(conf, test_names, Crand_TjNorm, Cfy_tjNorm, directory_path)
