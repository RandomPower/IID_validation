"""
This function plots the graph that compares the distribution of counters C0 obtained considering random sequences (aka read from file)
with those obtained through FY shuffling. For each test, the mean value of C0 is rapresented as a dot with errorbars one standard deviation long.
As expected, the two sets of results (random and shuffled) overlap, hinting towards the IID hypotesis.
The function 'scatterplot_RvsFY' takes as input:
    1) test: a dictionary with elements x:'name_of_test' (e.g. 0:'5.1.2:n_directional runs'). It is done as a dictionary only because I remembered
    that you used something alike to cycle among the tests, so I hope it could be convenient when putting everything together. If this is not the
    case, feel free to change the nature of 'test'. In such a case, the only modification of 'scatterplot_RvsFY' would in lines 24, 25, where test.values()
    is used as the x-values for the plot.
    2) C0r: a list containing the results of the counters C0 for each test using sequences read from file, i.e. C0r = [[counters C0 for test 5.1.2],[counters C0 for test 5.1.3],[counters C0 for test 5.1.4]...]
    3) C0fy: a list containing the results of the counters C0 for each test using sequences shuffled with FY, i.e. C0fy = [[counters C0 for test 5.1.2],[counters C0 for test 5.1.3],[counters C0 for test 5.1.4]...]

The function computes the mean and std for each list making up C0r and C0fy and uses the results for the plot.
"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from architecture.utils.config import n_sequences_stat, test_list, ref_numbers
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
                fy = "/Users/olivia1/Desktop/random_power_entropy_val_new/architecture/results/counters_distribution" \
                     "/FYShuffleTjNorm/fyShuffleTjNorm_" + str(test_list[ref]).strip() + ".csv"
                rand = "/Users/olivia1/Desktop/random_power_entropy_val_new/architecture/results/counters_distribution" \
                       "/RandomTjNorm/randomTjNorm_" + str(test_list[ref]).strip() + ".csv"
            else:
                fy = "/Users/olivia1/Desktop/random_power_entropy_val_new/architecture/results/counters_distribution" \
                     "/FYShuffleTx/fyShuffleTx_" + str(test_list[ref]).strip() + ".csv"
                rand = "/Users/olivia1/Desktop/random_power_entropy_val_new/architecture/results/counters_distribution" \
                       "/RandomTx/randomTx_" + str(test_list[ref]).strip() + ".csv"
            if not os.path.exists(fy) or not os.path.exists(rand):
                print(f"Error: File(s) for reference number {ref} do not exist.")
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
                print(f'Error reading or processing files for {test_list[ref]}: {e}')
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
