import datetime
import logging
import os
import sys

import pandas as pd

import permutation_tests
import utils.config
import utils.plot
import utils.useful_functions


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
        if not os.path.exists(fy) or not os.path.exists(rand):
            logging.error("File(s) for reference number %s do not exist.", ref)
            sys.exit(1)

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
            sys.exit(1)
    return C0_fy, C0_random


def comparison_scatterplot():
    """Plots the comparison scatterplot between FY_shuffle counters and reading from file.
    The counters values are read from csv files.
    """
    test_indexes = utils.config.config_data['statistical_analysis']['ref_numbers']
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
