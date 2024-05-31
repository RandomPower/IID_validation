import argparse
import contextlib
import datetime
import logging
import os
import time

import numpy as np
from tqdm import tqdm

import permutation_tests
import statistical_analysis
import utils.config
import utils.plot
import utils.read
import utils.save


def iid_plots(conf: utils.config.Config, Tx: list[float], Ti: list[list[float]]) -> None:
    """Plots a histogram of Ti values with respect to the Tx test value.

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    Tx : list of float
        reference test values
    Ti : list of list of float
        test values calculated on shuffled sequences
    """
    histo_dir = "histogram_TxTi"
    # Ensure the directory exists
    os.makedirs(histo_dir, exist_ok=True)

    Ti_transposed = np.transpose(Ti)
    test_names = utils.save.TestResults.test_labels(conf.nist.selected_tests, conf.nist.p)
    for t in range(len(Tx)):
        utils.plot.histogram_TxTi(Tx[t], Ti_transposed[t], test_names[t], histo_dir)


def iid_test_function(conf: utils.config.Config) -> None:
    """Performs the IID validation procedure.

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    """
    logger.debug("IID validation started")
    S = utils.read.read_file(conf.input_file, conf.nist.n_symbols, first_seq=conf.nist.first_seq)
    logger.debug("Read a sequence of %s symbols from file (%s) ", conf.nist.n_symbols, conf.input_file)

    logger.debug("Calculating the selected test reference statistics (Tx) on the input sequence")
    Tx = permutation_tests.run_tests(S, conf.nist.p, conf.nist.selected_tests)
    logger.debug("Reference statistics calculated!")

    logger.debug(
        "Calculating the selected test statistics (Ti) over %s permutations of the input sequence",
        conf.nist.n_permutations,
    )
    t0 = time.process_time()
    Ti = permutation_tests.run_tests_permutations(
        S, conf.nist.n_permutations, conf.nist.selected_tests, conf.nist.p, conf.parallel
    )
    ti = time.process_time() - t0
    logger.debug("Calculated the test statistic (Ti) on each shuffled sequence!")

    utils.save.TestResults.to_binary_file("test_values.bin", conf.nist.selected_tests, Tx, Ti, conf.nist.p)

    logger.debug("Calculating the counters, C0 and C1")
    C0, C1 = permutation_tests.calculate_counters(Tx, Ti)
    logger.debug("C0 = %s", C0)
    logger.debug("C1 = %s", C1)

    logger.debug("Validating IID assumption")
    IID_assumption = permutation_tests.iid_result(C0, C1, conf.nist.n_permutations)

    logger.info("IID assumption %s\n", "validated" if IID_assumption else "rejected")
    # save results of the IID validation
    utils.save.save_counters(
        conf.nist.n_symbols,
        conf.nist.n_permutations,
        conf.nist.selected_tests,
        C0,
        C1,
        IID_assumption,
        ti,
    )

    # plots
    if conf.nist.plot:
        logger.debug("Saving the Tx-Ti plots")
        iid_plots(conf, Tx, Ti)
        logger.debug("Tx-Ti plots saved!\n")


def statistical_analysis_function(conf: utils.config.Config) -> None:
    """Performs the statistical analysis procedure.

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    """
    stat_tests_names = [permutation_tests.tests[t].name for t in conf.stat.selected_tests]
    logger.debug("STATISTICAL ANALYSIS FOR TESTS %s", stat_tests_names)
    S = utils.read.read_file(conf.input_file, conf.stat.n_symbols)
    logger.debug("Read a sequence of %s symbols from file (%s) ", conf.stat.n_symbols, conf.input_file)

    logger.debug("Calculating the selected test reference statistics (Tx) on the input sequence")
    Tx = permutation_tests.run_tests(S, [conf.stat.p], conf.stat.selected_tests)
    logger.debug("Reference statistics calculated!")

    logger.debug("Building the counter's population")
    counters_C0_Tx = [[]] * conf.stat.n_iterations
    counters_C0_TjNorm = [[]] * conf.stat.n_iterations
    for i in tqdm(range(conf.stat.n_iterations)):
        # Calculate counters for Tx and TjNorm methods
        t0 = time.process_time()
        Ti = permutation_tests.run_tests_permutations(
            S, conf.stat.n_permutations, conf.stat.selected_tests, [conf.stat.p], conf.parallel
        )
        t1 = time.process_time()
        C0_Tx, C1_Tx = permutation_tests.calculate_counters(Tx, Ti)
        t2 = time.process_time()
        C0_TjNorm, C1_TjNorm = statistical_analysis.calculate_counters_TjNorm(conf, S, Ti)
        t3 = time.process_time()
        IID_assumption_Tx = permutation_tests.iid_result(C0_Tx, C1_Tx, conf.stat.n_permutations)
        IID_assumption_TjNorm = permutation_tests.iid_result(C0_TjNorm, C1_TjNorm, int(conf.stat.n_permutations / 2))
        # Save the values of the counters
        utils.save.save_counters(
            conf.stat.n_symbols,
            conf.stat.n_permutations,
            conf.stat.selected_tests,
            C0_Tx,
            C1_Tx,
            IID_assumption_Tx,
            t2 - t0,
            "countersTx_distribution",
        )
        utils.save.save_counters(
            conf.stat.n_symbols,
            conf.stat.n_permutations,
            conf.stat.selected_tests,
            C0_TjNorm,
            C1_TjNorm,
            IID_assumption_TjNorm,
            t3 - t2 + t1 - t0,
            "countersTjNorm_distribution",
        )

        counters_C0_Tx[i] = C0_Tx
        counters_C0_TjNorm[i] = C0_TjNorm

    logger.info("Counters population built!")

    # Plot the distributions of the counters
    for t in range(len(conf.stat.selected_tests)):
        utils.plot.counters_distribution_Tx(
            [i[t] for i in counters_C0_Tx],
            conf.stat.n_permutations,
            conf.stat.n_iterations,
            conf.stat.selected_tests[t],
        )
        utils.plot.counters_distribution_Tj(
            [i[t] for i in counters_C0_TjNorm],
            conf.stat.n_permutations,
            conf.stat.n_iterations,
            conf.stat.selected_tests[t],
        )

    logger.debug("Statistical analysis completed")


def main() -> None:
    parser = argparse.ArgumentParser()

    # Global
    global_args = parser.add_argument_group("[global]", "Global settings")
    global_args.add_argument("-c", "--config", type=str, help="Path to the TOML configuration file.")
    global_args.add_argument("-i", "--input_file", type=str, help="Path to the random bit file.")
    global_args.add_argument(
        "-t",
        "--nist_test",
        action=argparse.BooleanOptionalAction,
        help="Run the NIST IID test suite on a sequence obtained from the input file "
        f"[Default: {utils.config.Config.DEFAULT_NIST_TEST}].",
    )
    global_args.add_argument(
        "-a",
        "--stat_analysis",
        action=argparse.BooleanOptionalAction,
        help="Run the RaP statistical analysis on the input file "
        f"[Default: {utils.config.Config.DEFAULT_STATISTICAL_ANALYSIS}].",
    )
    global_args.add_argument(
        "--parallel",
        action=argparse.BooleanOptionalAction,
        help=f"Run the program in parallel mode [Default: {utils.config.Config.DEFAULT_PARALLEL}].",
    )
    global_args.add_argument(
        "-d",
        "--debug",
        action=argparse.BooleanOptionalAction,
        help=f"Show debug messages [Default: {utils.config.Config.DEFAULT_DEBUG}].",
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

    # Mutual exclusion between 'first_seq' and 'last_seq'
    first_seq_args = nist_args.add_mutually_exclusive_group()

    first_seq_args.add_argument(
        "--first_seq",
        default=None,
        action="store_true",
        help="Test the first sequence of [nist_n_symbols] symbols from the input file "
        f"[Default: {utils.config.Config.NISTConfig.DEFAULT_FIRST_SEQ}].",
    )
    first_seq_args.add_argument(
        "--last_seq",
        default=None,
        action="store_false",
        dest="first_seq",
        help="Test the last sequence of [nist_n_symbols] symbols from the input file "
        f"[Default: {not utils.config.Config.NISTConfig.DEFAULT_FIRST_SEQ}].",
    )
    nist_args.add_argument(
        "--plot",
        action=argparse.BooleanOptionalAction,
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
        "--stat_n_permutations",
        type=int,
        help=f"Number of sequences [Default: {utils.config.Config.StatConfig.DEFAULT_N_PERMUTATIONS}].",
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

        if conf.debug:
            s_handler.setLevel(logging.DEBUG)
        else:
            s_handler.setLevel(logging.INFO)

        np.set_printoptions(suppress=True, threshold=np.inf, linewidth=np.inf, formatter={"float": "{:0.6f}".format})

        utils.config.file_info(conf)
        utils.config.config_info(conf)

        if conf.nist_test:
            os.makedirs("IID_validation", exist_ok=True)
            with contextlib.chdir("IID_validation"):
                iid_test_function(conf)
        if conf.statistical_analysis:
            os.makedirs("statistical_analysis", exist_ok=True)
            with contextlib.chdir("statistical_analysis"):
                statistical_analysis_function(conf)


# Configure application logger
logger = logging.getLogger("IID_validation")

if __name__ == "__main__":
    main()
