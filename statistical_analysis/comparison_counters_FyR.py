import logging
import os
import sys

import pandas as pd

import utils.config
import utils.plot


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
    list of lists of int, list of lists of int and list of str
        counters values and list of test names
    """
    # Construct the filenames based on reference numbers
    C0_fy = []
    C0_random = []
    for ref in ref_numbers:
        if ref in utils.config.config_data["test_list"]:
            if Tj_norm:
                fy = os.path.abspath(
                    os.path.join(
                        "results",
                        "counters_distribution",
                        "FYShuffleTjNorm",
                        f"fyShuffleTjNorm_{str(utils.config.config_data['test_list'][ref]).strip()}.csv",
                    )
                )
                rand = os.path.abspath(
                    os.path.join(
                        "results",
                        "counters_distribution",
                        "RandomTjNorm",
                        f"randomTjNorm_{str(utils.config.config_data['test_list'][ref]).strip()}.csv",
                    )
                )
            else:
                fy = os.path.abspath(
                    os.path.join(
                        "results",
                        "counters_distribution",
                        "FYShuffleTx",
                        f"fyShuffleTx_{str(utils.config.config_data['test_list'][ref]).strip()}.csv",
                    )
                )
                rand = os.path.abspath(
                    os.path.join(
                        "results",
                        "counters_distribution",
                        "RandomTx",
                        f"randomTx_{str(utils.config.config_data['test_list'][ref]).strip()}.csv",
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
                logging.error(
                    "Reading or processing files for %s: %s not successful",
                    utils.config.config_data["test_list"][ref],
                    e,
                )
                sys.exit(1)
    return C0_fy, C0_random, [utils.config.config_data["test_list"][i] for i in ref_numbers]


def comparison_scatterplot():
    """Plots the comparison scatterplot between FY_shuffle counters and reading from file.
    The counters values are read from csv files.
    """
    Cfy, Crand, l1 = get_data(utils.config.config_data["statistical_analysis"]["ref_numbers"], False)
    Cfy_tjNorm, Crand_TjNorm, l2 = get_data(
        utils.config.config_data["statistical_analysis"]["ref_numbers"], True
    )

    utils.plot.scatterplot_RvsFY(l1, Crand, Cfy)
    utils.plot.scatterplot_RvsFY_TjNorm(l2, Crand_TjNorm, Cfy_tjNorm)
