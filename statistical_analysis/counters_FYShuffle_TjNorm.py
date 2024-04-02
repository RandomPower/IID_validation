import logging
import os
import time

from tqdm import tqdm

import utils.config
import utils.plot
import utils.shuffles
import utils.useful_functions


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
    for k in tqdm(range(utils.config.config_data["statistical_analysis_variables"]["n_iterations_c_stat"])):
        Ti = []
        seq = utils.shuffles.FY_shuffle(S.copy())
        C0 = 0
        C1 = 0
        if (
            utils.config.config_data["statistical_analysis_variables"]["distribution_test_index"] == 8
            or utils.config.config_data["statistical_analysis_variables"]["distribution_test_index"] == 9
        ):
            Ti.append(
                utils.useful_functions.execute_function(
                    utils.config.config_data["test_list"][
                        utils.config.config_data["statistical_analysis_variables"]["distribution_test_index"]
                    ],
                    seq,
                    utils.config.config_data["statistical_analysis_variables"]["p_value_stat"],
                )
            )
        else:
            Ti.append(
                utils.useful_functions.execute_function(
                    utils.config.config_data["test_list"][
                        utils.config.config_data["statistical_analysis_variables"]["distribution_test_index"]
                    ],
                    seq,
                    None,
                )
            )
        j = 1
        while j < utils.config.config_data["statistical_analysis_variables"]["n_sequences_stat"]:
            seq = utils.shuffles.FY_shuffle(S.copy())
            if (
                utils.config.config_data["statistical_analysis_variables"]["distribution_test_index"] == 8
                or utils.config.config_data["statistical_analysis_variables"]["distribution_test_index"] == 9
            ):
                t = utils.useful_functions.execute_function(
                    utils.config.config_data["test_list"][
                        utils.config.config_data["statistical_analysis_variables"]["distribution_test_index"]
                    ],
                    seq,
                    utils.config.config_data["statistical_analysis_variables"]["p_value_stat"],
                )
            else:
                t = utils.useful_functions.execute_function(
                    utils.config.config_data["test_list"][
                        utils.config.config_data["statistical_analysis_variables"]["distribution_test_index"]
                    ],
                    seq,
                    None,
                )
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
    """Calculates counter 0 and counter 1 list of values considering a series of sequences obtained via FY-shuffle from a starting one,
    save the values in a file and plot the distribution

    Parameters
    ----------
    S : list of int
        sequence of sample values
    """
    logging.debug("\nStatistical analysis FISHER YATES SHUFFLE WITH NORMALIZED Tj")
    f = os.path.abspath(
        os.path.join(
            "results",
            "counters_distribution",
            "FYShuffleTjNorm",
            f"fyShuffleTjNorm_{utils.config.config_data['test_list'][utils.config.config_data['statistical_analysis_variables']['distribution_test_index']]}.csv",
        )
    )
    t = time.process_time()
    C0, C1 = counters_FY_TjNorm(S)
    elapsed_time = time.process_time() - t

    # Saving results in test.csv
    utils.useful_functions.save_counters(C0, C1, elapsed_time, "FY_shuffle", f)

    # Plot results
    utils.plot.counters_distribution_Tj(
        C0,
        utils.config.config_data["statistical_analysis_variables"]["n_sequences_stat"],
        utils.config.config_data["statistical_analysis_variables"]["n_iterations_c_stat"],
        "FY_TjNorm",
    )
