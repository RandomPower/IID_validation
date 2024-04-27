import argparse
import concurrent.futures
import datetime
import logging
import os
import sys
import time

import numpy as np

import permutation_tests
import statistical_analysis
import utils.config
import utils.plot
import utils.read
import utils.shuffles
import utils.useful_functions


def calculate_counters(Tx, Ti):
    """Calculate counters values on a given sequence based on the condition provided by NIST

    Parameters
    ----------
    Tx : list of int
        reference test values
    Ti : list of int
        test values calculated on shuffled sequences

    Returns
    -------
    list of int, list of int
        counters lists
    """

    C0 = [0 for k in range(len(Tx))]
    C1 = [0 for k in range(len(Tx))]

    for u in range(len(Tx)):
        for t in range(len(Ti)):
            if Tx[u] > Ti[t][u]:
                C0[u] += 1
            if Tx[u] == Ti[t][u]:
                C1[u] += 1

    return C0, C1


def iid_result(C0, C1, Tx, n_sequences: int):
    """Determine whether the sequence is IID by checking that the value of the reference result Tx is between 0.05% and
    99.95% of the results Ti for the rest of the population of n_sequences sequences.

    Parameters
    ----------
    C0 : list of int
        counter 0
    C1 : list of int
        counter 1
    Tx : list of int
        reference test values
    n_sequences : int
        number of sequences in the population

    Returns
    -------
    bool
        iid result
    """
    IID = True
    for b in range(len(Tx)):
        if (C0[b] + C1[b] <= 0.0005 * n_sequences) or (C0[b] >= 0.9995 * n_sequences):
            IID = False
            break
    return IID


def FY_test_mode_parallel(conf: utils.config.Config, seq: list[int]):
    """Executes NIST test suite on shuffled sequence in parallel along n_sequences iterations

    Parameters
    ----------
    sequence : ist of int
        sequence of sample values

    Returns
    -------
    list of float
        list of test outputs
    """
    Ti = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for iteration in range(conf.nist.n_sequences):
            s_shuffled = permutation_tests.FY_shuffle(seq.copy())
            future = executor.submit(
                permutation_tests.run_tests,
                s_shuffled,
                conf.nist.pvalues,
                conf.nist.selected_tests,
            )
            futures.append(future)

        completed = 0
        total_futures = len(futures)
        for future in concurrent.futures.as_completed(futures):
            Ti.append(future.result())
            completed += 1
            percentage_complete = (completed / total_futures) * 100
            sys.stdout.write(f"\rProgress: {percentage_complete:.2f}%")
            sys.stdout.flush()
    return Ti


def iid_plots(conf: utils.config.Config, Tx, Ti):
    """Plot histogram and scatterplot of Ti values with respect to the Tx test value

    Parameters
    ----------
    Tx : list of int
        reference test values
    Ti : list of int
        test values calculated on shuffled sequences
    """
    sc_dir = "results/plots/scatterplot_TxTi"
    hist_dir = "results/plots/histogram_TxTi"
    current_run_date = datetime.datetime.now().strftime("%Y-%m-%d")
    dir_sc_run = os.path.join(
        sc_dir, current_run_date, str(utils.useful_functions.get_next_run_number(sc_dir, current_run_date))
    )
    dir_hist_run = os.path.join(
        hist_dir, current_run_date, str(utils.useful_functions.get_next_run_number(hist_dir, current_run_date))
    )

    # Ensure the directory exists
    os.makedirs(dir_sc_run, exist_ok=True)
    os.makedirs(dir_hist_run, exist_ok=True)

    Ti_transposed = np.transpose(Ti)
    for t in range(len(Tx)):
        if conf.nist.pvalues == conf.nist.DEFAULT_PVALUES:
            # Handle the special case for test 8 ('periodicity')
            if 8 <= t <= 12:
                p_index = t - 8  # Adjust index to map to the correct p value
                test_name = f"{permutation_tests.tests[8].name} (p={conf.nist.pvalues[p_index]})"
            # Handle the special case for test 9 ('covariance')
            elif 13 <= t <= 17:
                p_index = t - 13  # Adjust index to map to the correct p value
                test_name = f"{permutation_tests.tests[9].name} (p={conf.nist.pvalues[p_index]})"
            # For the values that should correspond to test 10 ('compression')
            elif t == 18:
                test_name = permutation_tests.tests[10].name  # Direct mapping for 'compression'
            else:
                # Direct mapping for other tests
                test_name = permutation_tests.tests[t].name
            utils.plot.histogram_TxTi(Tx[t], Ti_transposed[t], test_name, dir_hist_run)
            utils.plot.scatterplot_TxTi(conf, Tx[t], Ti_transposed[t], test_name, dir_sc_run)
        elif len(conf.nist.pvalues) == 1:
            utils.plot.histogram_TxTi(Tx[t], Ti_transposed[t], permutation_tests.tests[t].name, dir_hist_run)
            utils.plot.scatterplot_TxTi(conf, Tx[t], Ti_transposed[t], permutation_tests.tests[t].name, dir_sc_run)
        else:
            raise Exception("Support for arbitrary p values not implemented yet")


def iid_test_function(conf: utils.config.Config):
    logging.debug("NIST TEST")
    logging.debug("Process started")
    S = utils.read.read_file(conf.input_file, conf.nist.n_symbols, conf.nist.first_seq)
    logging.debug("Sequence calculated: S")

    logging.debug("Calculating for each test the reference statistic: Tx")
    Tx = permutation_tests.run_tests(S, conf.nist.pvalues, conf.nist.selected_tests)
    logging.debug("Reference statistics calculated!")

    logging.debug("Calculating each test statistic for each shuffled sequence: Ti")
    t0 = time.process_time()
    Ti = FY_test_mode_parallel(conf, S)
    ti = time.process_time() - t0
    logging.debug("Shuffled sequences Ti statistics calculated")

    C0, C1 = calculate_counters(Tx, Ti)
    logging.debug("C0 = %s", C0)
    logging.debug("C1 = %s", C1)

    IID_assumption = iid_result(C0, C1, Tx, conf.nist.n_sequences)

    logging.info("IID assumption %s", "validated" if IID_assumption else "rejected")
    # save results of the IID validation
    utils.useful_functions.save_IID_validation(conf, C0, C1, IID_assumption, ti)

    # plots
    if conf.nist.plot:
        iid_plots(conf, Tx, Ti)


def statistical_analysis_function(conf: utils.config.Config):
    logging.debug("----------------------------------------------------------------\n \n")
    logging.debug("STATISTICAL ANALYSIS FOR TEST %s", permutation_tests.tests[conf.stat.distribution_test_index].name)
    S = utils.read.read_file(conf.input_file, conf.stat.n_symbols, True)
    logging.debug("Sequence calculated: S")
    with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
        tasks = [
            executor.submit(statistical_analysis.FY_Tx, S, conf),
            executor.submit(statistical_analysis.FY_TjNorm, S, conf),
            executor.submit(statistical_analysis.Random_Tx, S, conf),
            executor.submit(statistical_analysis.Random_TjNorm, S, conf),
        ]
        # Wait for all tasks to complete
        for task in tasks:
            task.result()

    statistical_analysis.comparison_scatterplot(conf)
    logging.debug("Statistical analysis completed.")


def main():
    parser = argparse.ArgumentParser()

    # Global
    global_args = parser.add_argument_group("[global]", "global settings")
    global_args.add_argument("-c", "--config", type=str, help="Configuration file")
    global_args.add_argument("-i", "--input_file", type=str, help="Random bit file.")
    global_args.add_argument("-t", "--test_nist", action="store_true", help="IID validation test.")
    global_args.add_argument("-a", "--stat_analysis", action="store_true", help="Statistical analysis.")

    # Nist test
    nist_args = parser.add_argument_group("[nist_test]", "nist IID test suite configuration")
    nist_args.add_argument(
        "--nist_selected_tests", metavar="INDEX", nargs="+", type=int, help="Selection of test numbers to execute."
    )
    nist_args.add_argument("--nist_n_symbols", type=int, help="Number of symbols in the random-bit sequence.")
    nist_args.add_argument(
        "--nist_n_sequences", type=int, help="Number of sequences on which the test will be carried out."
    )
    nist_args.add_argument("--shuffle", action="store_true", help="Fisher-Yates shuffle.")
    nist_args.add_argument(
        "--first_seq", action="store_true", help="Read the sequence from the start of the input file."
    )
    nist_args.add_argument("--plot", action="store_true", help="See plots.")
    nist_args.add_argument("--pvalues", metavar="P", nargs="+", type=int, help="User-defined p-value.")

    # Statistical analysis
    stat_args = parser.add_argument_group("[statistical_analysis]", "statistical analysis options")
    stat_args.add_argument("--stat_n_sequences", type=int, help="Number of sequences for the statistical analysis.")
    stat_args.add_argument(
        "--stat_n_symbols", type=int, help="Number of symbols in a sequence for the statistical analysis."
    )
    stat_args.add_argument(
        "--stat_n_iter_c", type=int, help="Number of iterations to do on sequences for the stat analysis."
    )
    stat_args.add_argument("--distr_test_idx", metavar="INDEX", type=int, help="Test to execute.")
    stat_args.add_argument("--stat_shuffle", action="store_true", help="Produce sequences using Fisher-Yates.")
    stat_args.add_argument(
        "--stat_pvalue", metavar="P", type=int, help="User-defined p-value for the statistical analysis."
    )
    stat_args.add_argument(
        "--ref_nums",
        metavar="INDEX",
        nargs="+",
        type=int,
        help="Tests to consider for comparing the stat results.",
    )

    args = parser.parse_args()
    conf = utils.config.Config(args)

    logging.basicConfig(
        filename="IID_validation.log",
        filemode="w",
        format="%(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )

    np.set_printoptions(suppress=True, threshold=np.inf, linewidth=np.inf, formatter={"float": "{:0.6f}".format})

    utils.config.file_info(conf)
    utils.config.config_info(conf)
    if conf.nist_test:
        iid_test_function(conf)

    if conf.statistical_analysis:
        statistical_analysis_function(conf)


if __name__ == "__main__":
    main()
