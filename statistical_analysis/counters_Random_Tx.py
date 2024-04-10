import datetime
import logging
import os
import time

from tqdm import tqdm

import permutation_tests
import utils.config
import utils.plot
import utils.shuffles
import utils.useful_functions


def counters_Random_Tx(S, test):
    """Compute the counters C0 and C1 for a given test on a series of random sequences read from file.
    The given test is performed on the first sequence to obtain the reference value: C0 is incremented if the result
    of the test T computed on a sequence is bigger than that it, C1 is incremented if they are equal.

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    list of int, list of int
        counter 0 and counter 1 lists of values
    """

    if test in [8, 9]:
        Tx = permutation_tests.tests[test].run(S, utils.config.config_data['statistical_analysis']['p_value_stat'])
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
                Ti.append(permutation_tests.tests[test].run(k, utils.config.config_data['statistical_analysis']['p_value_stat']))
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
    distribution_test_index = utils.config.config_data['statistical_analysis']['distribution_test_index']
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
