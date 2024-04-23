import datetime
import logging
import os
import sys
import time

import pandas as pd
from tqdm import tqdm

import permutation_tests
import utils.config
import utils.plot
import utils.shuffles
import utils.useful_functions


def counters_FYShuffle_Tx(S, test):
    """Compute the counters C0 and C1 for a given test on a series of sequences obtained via FY-shuffle from a starting
    one. The given test is performed on the first sequence to obtain the reference value:
    C0 is incremented if the result of the test T computed on a sequence is bigger than that it,
    C1 is incremented if they are equal.

    Parameters
    ----------
    S : list of int
        sequence of sample values
    test : int
        index of the test used to produce the counters

    Returns
    -------
    list of int, list of int
        counter 0 and counter 1 lists of values
    """
    counters_0 = []
    counters_1 = []
    # Calculate reference statistics
    if test in [8, 9]:
        Tx = permutation_tests.tests[test].run(S, utils.config.config_data["statistical_analysis"]["p_value_stat"])
    else:
        Tx = permutation_tests.tests[test].run(S)

    # S_shuffled will move by a P_pointer for every n_sequences
    for i in tqdm(range(utils.config.config_data["statistical_analysis"]["n_iterations_c_stat"])):
        C0 = 0
        C1 = 0
        Ti = []
        for k in range(utils.config.config_data["statistical_analysis"]["n_sequences_stat"]):
            s_shuffled = permutation_tests.FY_shuffle(S.copy())
            if test in [8, 9]:
                Ti.append(
                    permutation_tests.tests[test].run(
                        s_shuffled, utils.config.config_data["statistical_analysis"]["p_value_stat"]
                    )
                )
            else:
                Ti.append(permutation_tests.tests[test].run(s_shuffled))

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
    """Calculates counter 0 and counter 1 list of values considering a series of sequences obtained via FY-shuffle from
    a starting one, save the values in a file and plot the distribution

    Parameters
    ----------
    S : list of int
        sequence of sample values
    """
    logging.debug("Statistical analysis FISHER YATES SHUFFLE FOR Tx VALUES")
    distribution_test_index = utils.config.config_data["statistical_analysis"]["distribution_test_index"]
    f = os.path.abspath(
        os.path.join(
            "results",
            "counters_distribution",
            "FYShuffleTx",
            f"fyShuffleTx_{permutation_tests.tests[distribution_test_index].name}.csv",
        )
    )
    t = time.process_time()
    C0, C1 = counters_FYShuffle_Tx(S, distribution_test_index)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    utils.useful_functions.save_counters(C0, C1, elapsed_time, "FY_shuffle", f)

    # Plot results
    # Define directory path
    plot_dir = "results/plots/counters_FYShuffle_Tx"
    current_run_date = datetime.datetime.now().strftime("%Y-%m-%d")
    dir_plot_run = os.path.join(
        plot_dir, current_run_date, str(utils.useful_functions.get_next_run_number(plot_dir, current_run_date))
    )
    # Ensure the directory exists
    os.makedirs(dir_plot_run, exist_ok=True)

    utils.plot.counters_distribution_Tx(
        C0,
        utils.config.config_data["statistical_analysis"]["n_sequences_stat"],
        utils.config.config_data["statistical_analysis"]["n_iterations_c_stat"],
        "FY_Tx",
        dir_plot_run,
    )


def counters_Random_Tx(S, test):
    """Compute the counters C0 and C1 for a given test on a series of random sequences read from file.
    The given test is performed on the first sequence to obtain the reference value: C0 is incremented if the result
    of the test T computed on a sequence is bigger than that it, C1 is incremented if they are equal.

    Parameters
    ----------
    S : list of int
        sequence of sample values
    test : int
        index of the test used to produce the counters

    Returns
    -------
    list of int, list of int
        counter 0 and counter 1 lists of values
    """

    if test in [8, 9]:
        Tx = permutation_tests.tests[test].run(S, utils.config.config_data["statistical_analysis"]["p_value_stat"])
    else:
        Tx = permutation_tests.tests[test].run(S)
    counters_0 = []
    counters_1 = []
    index = utils.config.config_data["statistical_analysis"]["n_symbols_stat"] / 2

    for i in tqdm(range(utils.config.config_data["statistical_analysis"]["n_iterations_c_stat"])):
        C0 = 0
        C1 = 0
        S_shuffled = utils.shuffles.shuffle_from_file(
            index,
            utils.config.config_data["statistical_analysis"]["n_symbols_stat"],
            utils.config.config_data["statistical_analysis"]["n_sequences_stat"],
        )
        Ti = []
        for k in S_shuffled:
            if test in [8, 9]:
                Ti.append(
                    permutation_tests.tests[test].run(
                        k, utils.config.config_data["statistical_analysis"]["p_value_stat"]
                    )
                )
            else:
                Ti.append(permutation_tests.tests[test].run(k))

        for z in range(len(Ti)):
            if Tx > Ti[z]:
                C0 += 1
            if Tx == Ti[z]:
                C1 += 1
        index += utils.config.config_data["statistical_analysis"]["n_sequences_stat"] * (
            utils.config.config_data["statistical_analysis"]["n_symbols_stat"] / 2
        )

        counters_0.append(C0)
        counters_1.append(C1)

    logging.debug("Random_Tx counter_0: %s", counters_0)
    logging.debug("Random_Tx counter_1: %s", counters_1)

    return counters_0, counters_1


def Random_Tx(S):
    """Calculates counter 0 and counter 1 list of values considering a series of random sequences read from file,
    save the values in a file and plot the distribution

    Parameters
    ----------
    S : list of int
        sequence of sample values
    """
    logging.debug("\nStatistical analysis RANDOM SAMPLING FROM FILE FOR Tx VALUES")
    distribution_test_index = utils.config.config_data["statistical_analysis"]["distribution_test_index"]
    f = os.path.abspath(
        os.path.join(
            "results",
            "counters_distribution",
            "RandomTx",
            f"RandomTx_{permutation_tests.tests[distribution_test_index].name}.csv",
        )
    )
    t = time.process_time()
    C0, C1 = counters_Random_Tx(S, distribution_test_index)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    utils.useful_functions.save_counters(C0, C1, elapsed_time, "Shuffle_from_file", f)

    # Plot results
    # Define directory path
    plot_dir = "results/plots/counters_Random_Tx"
    current_run_date = datetime.datetime.now().strftime("%Y-%m-%d")
    dir_plot_run = os.path.join(
        plot_dir, current_run_date, str(utils.useful_functions.get_next_run_number(plot_dir, current_run_date))
    )
    # Ensure the directory exists
    os.makedirs(dir_plot_run, exist_ok=True)

    utils.plot.counters_distribution_Tx(
        C0,
        utils.config.config_data["statistical_analysis"]["n_sequences_stat"],
        utils.config.config_data["statistical_analysis"]["n_iterations_c_stat"],
        "Random_Tx",
        dir_plot_run,
    )


def counters_FY_TjNorm(S, test):
    """Compute the counters C0 and C1 for a given test on a series of sequences obtained via FY-shuffle from a starting
    one. C0 is incremented if the result of the test T on a sequence is bigger than that on the following sequence; if
    the results of the test are equal the second sequence is ignored.
    Each pair of sequences is considered as disjointed from the following one.


    Parameters
    ----------
    S : list of int
        sequence of sample values
    test : int
        index of the test used to produce the counters

    Returns
    -------
    list of int, list of int
        counter 0 and counter 1 lists of values
    """
    counters_0 = []
    counters_1 = []
    for k in tqdm(range(utils.config.config_data["statistical_analysis"]["n_iterations_c_stat"])):
        Ti = []
        seq = permutation_tests.FY_shuffle(S.copy())
        C0 = 0
        C1 = 0
        if test in [8, 9]:
            Ti.append(
                permutation_tests.tests[test].run(
                    seq, utils.config.config_data["statistical_analysis"]["p_value_stat"]
                )
            )
        else:
            Ti.append(permutation_tests.tests[test].run(seq))
        j = 1
        while j < utils.config.config_data["statistical_analysis"]["n_sequences_stat"]:
            seq = permutation_tests.FY_shuffle(S.copy())
            if test in [8, 9]:
                t = permutation_tests.tests[test].run(
                    seq, utils.config.config_data["statistical_analysis"]["p_value_stat"]
                )
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

    logging.debug("FY_TjNorm counter_0: %s", counters_0)
    logging.debug("FY_TjNorm counter_1: %s", counters_1)

    return counters_0, counters_1


def FY_TjNorm(S):
    """Calculates counter 0 and counter 1 list of values considering a series of sequences obtained via FY-shuffle from
    a starting one, save the values in a file and plot the distribution

    Parameters
    ----------
    S : list of int
        sequence of sample values
    """
    logging.debug("\nStatistical analysis FISHER YATES SHUFFLE WITH NORMALIZED Tj")
    distribution_test_index = utils.config.config_data["statistical_analysis"]["distribution_test_index"]
    f = os.path.abspath(
        os.path.join(
            "results",
            "counters_distribution",
            "FYShuffleTjNorm",
            f"fyShuffleTjNorm_{permutation_tests.tests[distribution_test_index].name}.csv",
        )
    )
    t = time.process_time()
    C0, C1 = counters_FY_TjNorm(S, distribution_test_index)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    utils.useful_functions.save_counters(C0, C1, elapsed_time, "FY_shuffle", f)

    # Plot results
    # Define directory path
    plot_dir = "results/plots/counters_FYShuffle_TjNorm"
    current_run_date = datetime.datetime.now().strftime("%Y-%m-%d")
    dir_plot_run = os.path.join(
        plot_dir, current_run_date, str(utils.useful_functions.get_next_run_number(plot_dir, current_run_date))
    )
    # Ensure the directory exists
    os.makedirs(dir_plot_run, exist_ok=True)

    utils.plot.counters_distribution_Tj(
        C0,
        utils.config.config_data["statistical_analysis"]["n_sequences_stat"],
        utils.config.config_data["statistical_analysis"]["n_iterations_c_stat"],
        "FY_TjNorm",
        dir_plot_run,
    )


def counters_random_TjNorm():
    """Compute the counters C0 and C1 for a given test on a series of random sequences read from file.
    C0 is incremented if the result of the test T on a sequence is bigger than that on the following sequence;
    if the results of the test are equal the second sequence is ignored.
    Each pair of sequences is considered as disjointed from the following one.

    Returns
    -------
    list of int, list of int
        counter 0 and counter 1 lists of values
    """
    counters_0 = []
    counters_1 = []
    index = 0

    for k in tqdm(range(utils.config.config_data["statistical_analysis"]["n_iterations_c_stat"])):
        C0 = 0
        C1 = 0
        s_sequences, Ti = utils.shuffles.shuffle_from_file_Norm(
            index,
            utils.config.config_data["statistical_analysis"]["n_symbols_stat"],
            utils.config.config_data["statistical_analysis"]["n_sequences_stat"],
            utils.config.config_data["statistical_analysis"]["distribution_test_index"],
        )

        for z in range(0, len(Ti) - 1, 2):
            if Ti[z] > Ti[z + 1]:
                C0 += 1
            if Ti[z] == Ti[z + 1]:
                C1 += 1

        counters_0.append(C0)
        counters_1.append(C1)
        index += (
            utils.config.config_data["statistical_analysis"]["n_sequences_stat"]
            * utils.config.config_data["statistical_analysis"]["n_symbols_stat"]
            / 2
        )

    logging.debug("Random_TjNorm counter_0: %s", counters_0)
    logging.debug("Random_TjNorm counter_1: %s", counters_1)

    return counters_0, counters_1


def Random_TjNorm(S, test):
    """Calculates counter 0 and counter 1 list of values considering a series of random sequences read from file,
    save the values in a file and plot the distribution

    Parameters
    ----------
    S : list of int
        sequence of sample values
    test : int
        index of the test used to produce the counters
    """
    logging.debug("\nStatistical analysis RANDOM SAMPLING FROM FILE WITH Tj NORMALIZED")
    f = os.path.abspath(
        os.path.join(
            "results",
            "counters_distribution",
            "RandomTjNorm",
            f"randomTjNorm_{permutation_tests.tests[test].name}.csv",
        )
    )
    t = time.process_time()
    C0, C1 = counters_random_TjNorm()
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    utils.useful_functions.save_counters(C0, C1, elapsed_time, "Shuffle_from_file", f)

    # Plot results
    # Define directory path
    plot_dir = "results/plots/counters_Random_TjNorm"
    current_run_date = datetime.datetime.now().strftime("%Y-%m-%d")
    dir_plot_run = os.path.join(
        plot_dir, current_run_date, str(utils.useful_functions.get_next_run_number(plot_dir, current_run_date))
    )
    # Ensure the directory exists
    os.makedirs(dir_plot_run, exist_ok=True)
    utils.plot.counters_distribution_Tj(
        C0,
        utils.config.config_data["statistical_analysis"]["n_sequences_stat"],
        utils.config.config_data["statistical_analysis"]["n_iterations_c_stat"],
        "Random_TjNorm",
        dir_plot_run,
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
            fy = os.path.abspath(
                os.path.join(
                    "results",
                    "counters_distribution",
                    "FYShuffleTjNorm",
                    f"fyShuffleTjNorm_{permutation_tests.tests[ref].name}.csv",
                )
            )
            rand = os.path.abspath(
                os.path.join(
                    "results",
                    "counters_distribution",
                    "RandomTjNorm",
                    f"randomTjNorm_{permutation_tests.tests[ref].name}.csv",
                )
            )
        else:
            fy = os.path.abspath(
                os.path.join(
                    "results",
                    "counters_distribution",
                    "FYShuffleTx",
                    f"fyShuffleTx_{permutation_tests.tests[ref].name}.csv",
                )
            )
            rand = os.path.abspath(
                os.path.join(
                    "results",
                    "counters_distribution",
                    "RandomTx",
                    f"randomTx_{permutation_tests.tests[ref].name}.csv",
                )
            )
        if not os.path.exists(fy):
            logging.error("Results file for test number %s does not exist: %s", ref, fy)
            raise ValueError(f"Results file for test number {ref} does not exist: {fy}")
        if not os.path.exists(rand):
            logging.error("Results file for test number %s does not exist: %s", ref, rand)
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
            logging.error("Reading or processing files for %s: %s not successful", permutation_tests.tests[ref], e)
            raise e
    return C0_fy, C0_random


def comparison_scatterplot():
    """Plots the comparison scatterplot between FY_shuffle counters and reading from file.
    The counters values are read from csv files.
    """
    test_indexes = utils.config.config_data["statistical_analysis"]["ref_numbers"]
    test_names = [permutation_tests.tests[i].name for i in test_indexes]

    Cfy, Crand = get_data(test_indexes, False)
    Cfy_tjNorm, Crand_TjNorm = get_data(test_indexes, True)

    # Define directory where to save the plot
    comparison_dir = "results/plots/comparison_RvsFY"
    comparison_TjNorm_dir = "results/plots/comparison_RvsFY_TjNorm"
    current_run_date = datetime.datetime.now().strftime("%Y-%m-%d")
    dir_comparison_run = os.path.join(
        comparison_dir,
        current_run_date,
        str(utils.useful_functions.get_next_run_number(comparison_dir, current_run_date)),
    )
    dir_comparison_TjNorm_run = os.path.join(
        comparison_TjNorm_dir,
        current_run_date,
        str(utils.useful_functions.get_next_run_number(comparison_TjNorm_dir, current_run_date)),
    )

    # Ensure the directory exists
    os.makedirs(dir_comparison_run, exist_ok=True)
    os.makedirs(dir_comparison_TjNorm_run, exist_ok=True)

    # Plot the results
    utils.plot.scatterplot_RvsFY(test_names, Crand, Cfy, dir_comparison_run)
    utils.plot.scatterplot_RvsFY_TjNorm(test_names, Crand_TjNorm, Cfy_tjNorm, dir_comparison_TjNorm_run)
