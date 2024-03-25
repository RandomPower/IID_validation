import os
import sys
import pandas as pd
import logging
from architecture.utils.config import test_list, ref_numbers
from architecture.utils.plot import scatterplot_RvsFY, scatterplot_RvsFY_TjNorm


def get_data(ref_numbers, Tj_norm):
    """
    This function reads the file corresponding to the reference test numbers and returns the counters values
    :param ref_numbers: tests to compare
    :param Tj_norm: boolean
    :return: the counter values within the files
    """
    # Construct the filenames based on reference numbers
    C0_fy = []
    C0_random = []
    for ref in ref_numbers:
        if ref in test_list:
            if Tj_norm:
                fy = (
                    "/Users/olivia1/Desktop/random_power_entropy_val_new/architecture/results/counters_distribution"
                    "/FYShuffleTjNorm/fyShuffleTjNorm_" + str(test_list[ref]).strip() + ".csv"
                )
                rand = (
                    "/Users/olivia1/Desktop/random_power_entropy_val_new/architecture/results/counters_distribution"
                    "/RandomTjNorm/randomTjNorm_" + str(test_list[ref]).strip() + ".csv"
                )
            else:
                fy = (
                    "/Users/olivia1/Desktop/random_power_entropy_val_new/architecture/results/counters_distribution"
                    "/FYShuffleTx/fyShuffleTx_" + str(test_list[ref]).strip() + ".csv"
                )
                rand = (
                    "/Users/olivia1/Desktop/random_power_entropy_val_new/architecture/results/counters_distribution"
                    "/RandomTx/randomTx_" + str(test_list[ref]).strip() + ".csv"
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
                logging.error("Reading or processing files for %s: %s not successful", test_list[ref], e)
                sys.exit(1)
    return C0_fy, C0_random, [test_list[i] for i in ref_numbers]


def comparison_scatterplot():
    """
    This function produces the comparison scatterplot between FY_shuffle counters and Random sampling from
    the file. The counters values are read from previously produced csv files.
    """
    Cfy, Crand, l1 = get_data(ref_numbers, False)
    Cfy_tjNorm, Crand_TjNorm, l2 = get_data(ref_numbers, True)

    scatterplot_RvsFY(l1, Crand, Cfy)
    scatterplot_RvsFY_TjNorm(l2, Crand_TjNorm, Cfy_tjNorm)
