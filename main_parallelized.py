import argparse
import concurrent.futures
import contextlib
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
        C0[u], C1[u] = permutation_tests.get_C0_C1_Tx(Tx[u], [Ti[t][u] for t in range(len(Ti))])

    return C0, C1


def iid_result(C0: list[int], C1: list[int], n_sequences: int):
    """Determine whether the sequence is IID by checking that the value of the reference result Tx is between 0.05% and
    99.95% of the results Ti for the rest of the population of n_sequences sequences.

    Parameters
    ----------
    C0 : list of int
        counter 0
    C1 : list of int
        counter 1
    n_sequences : int
        number of sequences in the population

    Returns
    -------
    bool
        iid result
    """
    if len(C0) != len(C1):
        raise Exception(f"Counter lengths must match: C0 ({len(C0)}), C1 ({len(C1)})")
    for b in range(len(C0)):
        if (C0[b] + C1[b] <= 0.0005 * n_sequences) or (C0[b] >= 0.9995 * n_sequences):
            return False
    return True


def FY_test_mode_parallel(conf: utils.config.Config, S: list[int]):
    """Executes NIST test suite on shuffled sequence in parallel along n_permutations iterations

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    S : list of int
        sequence of sample values

    Returns
    -------
    list of float
        list of test outputs
    """
    Ti = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for iteration in range(conf.nist.n_permutations):
            s_shuffled = permutation_tests.FY_shuffle(S.copy())
            future = executor.submit(
                permutation_tests.run_tests,
                s_shuffled,
                conf.nist.p,
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
    """Plot histogram of Ti values with respect to the Tx test value

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    Tx : list of int
        reference test values
    Ti : list of int
        test values calculated on shuffled sequences
    """
    histo_dir = os.path.join("IID_validation", "histogram_TxTi")
    # Ensure the directory exists
    os.makedirs(histo_dir, exist_ok=True)

    Ti_transposed = np.transpose(Ti)
    for t in range(len(Tx)):
        if conf.nist.p == conf.nist.DEFAULT_P:
            # Handle the special case for test 8 ('periodicity')
            if 8 <= t <= 12:
                p_index = t - 8  # Adjust index to map to the correct p value
                test_name = f"{permutation_tests.tests[8].name} (p={conf.nist.p[p_index]})"
            # Handle the special case for test 9 ('covariance')
            elif 13 <= t <= 17:
                p_index = t - 13  # Adjust index to map to the correct p value
                test_name = f"{permutation_tests.tests[9].name} (p={conf.nist.p[p_index]})"
            # For the values that should correspond to test 10 ('compression')
            elif t == 18:
                test_name = permutation_tests.tests[10].name  # Direct mapping for 'compression'
            else:
                # Direct mapping for other tests
                test_name = permutation_tests.tests[t].name
            utils.plot.histogram_TxTi(Tx[t], Ti_transposed[t], test_name, histo_dir)
        elif len(conf.nist.p) == 1:
            utils.plot.histogram_TxTi(Tx[t], Ti_transposed[t], permutation_tests.tests[t].name, histo_dir)
        else:
            raise Exception("Support for arbitrary p values not implemented yet")


def iid_test_function(conf: utils.config.Config):
    """IID test function

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    """
    logger.debug("NIST TEST")
    logger.debug("Process started")
    S = utils.read.read_file(conf.input_file, conf.nist.n_symbols, conf.nist.first_seq)
    logger.debug("Sequence calculated: S")

    logger.debug("Calculating for each test the reference statistic: Tx")
    Tx = permutation_tests.run_tests(S, conf.nist.p, conf.nist.selected_tests)
    logger.debug("Reference statistics calculated!")

    logger.debug("Calculating each test statistic for each shuffled sequence: Ti")
    t0 = time.process_time()
    Ti = FY_test_mode_parallel(conf, S)
    ti = time.process_time() - t0
    logger.debug("Shuffled sequences Ti statistics calculated")

    C0, C1 = calculate_counters(Tx, Ti)
    logger.debug("C0 = %s", C0)
    logger.debug("C1 = %s", C1)

    IID_assumption = iid_result(C0, C1, conf.nist.n_permutations)

    logger.info("IID assumption %s", "validated" if IID_assumption else "rejected")
    # save results of the IID validation
    utils.useful_functions.save_IID_validation(conf, C0, C1, IID_assumption, ti)

    # plots
    if conf.nist.plot:
        iid_plots(conf, Tx, Ti)


def statistical_analysis_function(conf: utils.config.Config):
    """Statistical analysis function

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    """
    logger.debug("----------------------------------------------------------------\n \n")
    stat_tests_names = [permutation_tests.tests[t].name for t in conf.stat.selected_tests]
    logger.debug("STATISTICAL ANALYSIS FOR TESTS %s", stat_tests_names)
    S = utils.read.read_file(conf.input_file, conf.stat.n_symbols, True)
    logger.debug("Sequence calculated: S")
    for test in conf.stat.selected_tests:
        with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
            tasks = [
                executor.submit(statistical_analysis.counters_Tx, conf, S, test),
                executor.submit(statistical_analysis.counters_TjNorm, conf, S, test),
            ]
            # Wait for all tasks to complete
            for task in tasks:
                task.result()

    logger.debug("Statistical analysis completed.")


def main():
    parser = argparse.ArgumentParser()

    # Global
    global_args = parser.add_argument_group("[global]", "Global settings")
    global_args.add_argument("-c", "--config", type=str, help="Path to the TOML configuration file.")
    global_args.add_argument("-i", "--input_file", type=str, help="Path to the random bit file.")
    global_args.add_argument(
        "-t",
        "--nist_test",
        action="store_true",
        help="Run the NIST IID test suite on a sequence obtained from the input file.",
    )
    global_args.add_argument(
        "-a", "--stat_analysis", action="store_true", help="Run the RaP statistical analysis on the input file."
    )

    # Nist test
    nist_args = parser.add_argument_group("[nist_test]", "NIST IID test suite configuration")
    nist_args.add_argument(
        "--nist_selected_tests",
        metavar="INDEX",
        nargs="+",
        type=int,
        help="Indexes of the tests to execute. See README.md for the full list [Default: all].",
    )
    nist_args.add_argument(
        "--nist_n_symbols",
        type=int,
        help=f"Number of symbols in the input sequence [Default: {utils.config.Config.NISTConfig.DEFAULT_N_SYMBOLS}].",
    )
    nist_args.add_argument(
        "--nist_n_permutations",
        type=int,
        help="Number of permutations of the input sequence "
        f"[Default: {utils.config.Config.NISTConfig.DEFAULT_N_PERMUTATIONS}].",
    )
    nist_args.add_argument(
        "--first_seq",
        action="store_true",
        help=(
            "Test the first sequence of [nist_n_symbols] symbols from the input file "
            f"[Default: {utils.config.Config.NISTConfig.DEFAULT_FIRST_SEQ}]."
        ),
    )
    nist_args.add_argument(
        "--plot",
        action="store_true",
        help=(
            "Generate a histogram plot for each of the executed tests. "
            f"[Default: {utils.config.Config.NISTConfig.DEFAULT_PLOT}]"
        ),
    )
    nist_args.add_argument(
        "--nist_p",
        metavar="P",
        nargs="+",
        type=int,
        help=(
            "Lag parameters p used for periodicity and covariance tests "
            f"[Default: {utils.config.Config.NISTConfig.DEFAULT_P}]"
        ),
    )

    # Statistical analysis
    stat_args = parser.add_argument_group("[statistical_analysis]", "Statistical analysis options")
    stat_args.add_argument(
        "--stat_selected_tests",
        metavar="INDEX",
        nargs="+",
        type=int,
        help="Indexes of the tests to execute. See README.md for the full list [Default: all].",
    )
    stat_args.add_argument(
        "--stat_n_sequences",
        type=int,
        help=f"Number of sequences [Default: {utils.config.Config.StatConfig.DEFAULT_N_SEQUENCES}].",
    )
    stat_args.add_argument(
        "--stat_n_symbols",
        type=int,
        help=f"Number of symbols in a sequence [Default: {utils.config.Config.StatConfig.DEFAULT_N_SYMBOLS}].",
    )
    stat_args.add_argument(
        "--stat_n_iterations",
        type=int,
        help=(
            "Number of iterations of the IID test suite to obtain the statistical distribution of counter C0 "
            f"[Default: {utils.config.Config.StatConfig.DEFAULT_N_ITERATIONS}]."
        ),
    )
    stat_args.add_argument(
        "--stat_p",
        metavar="P",
        type=int,
        help="Single lag parameter p used for periodicity and covariance tests "
        f"[Default: {utils.config.Config.StatConfig.DEFAULT_P}]",
    )

    args = parser.parse_args()
    conf = utils.config.Config(args)

    # Create results folder and move into it
    current_run_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.path.join("results", current_run_date)
    os.makedirs(results_dir, exist_ok=True)
    with contextlib.chdir(results_dir):
        # Configure logging
        # Write all loggers to file, each with their own level, from DEBUG up
        f_handler = logging.FileHandler(f"{current_run_date}.log", mode="w")
        f_handler.setLevel(logging.DEBUG)
        f_handler.setFormatter(logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s"))
        logging.getLogger().addHandler(f_handler)

        # Write the application-specific logger to stderr, from INFO up
        s_handler = logging.StreamHandler()
        s_handler.setLevel(logging.INFO)
        s_handler.setFormatter(logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s"))
        logger.addHandler(s_handler)

        # Set application-specific logger level from DEBUG up
        logger.setLevel(logging.DEBUG)

        np.set_printoptions(suppress=True, threshold=np.inf, linewidth=np.inf, formatter={"float": "{:0.6f}".format})

        utils.config.file_info(conf)
        utils.config.config_info(conf)

        if conf.nist_test:
            iid_test_function(conf)
        if conf.statistical_analysis:
            statistical_analysis_function(conf)


# Configure application logger
logger = logging.getLogger("IID_validation")

if __name__ == "__main__":
    main()
