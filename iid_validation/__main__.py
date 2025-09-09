import argparse
import contextlib
import datetime
import enum
import importlib.metadata
import logging
import os
import sys
from pathlib import Path

import numpy as np

from . import config, iid_test, min_entropy, statistical_analysis


class ReturnValue(enum.IntEnum):
    OK = 0
    BAD_CONFIG = 1
    FAILED_ANALYSIS = 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=importlib.metadata.version(__spec__.parent))

    # Global
    global_args = parser.add_argument_group("[global]", "Global settings")
    global_args.add_argument("-c", "--config", type=str, help="Path to the TOML configuration file.")
    global_args.add_argument("-i", "--input_file", type=str, help="Path to the random bit file.")
    global_args.add_argument(
        "-t",
        "--nist_test",
        action=argparse.BooleanOptionalAction,
        help="Run the NIST IID test suite on a sequence obtained from the input file "
        f"[Default: {config.Config.DEFAULT_NIST_TEST}].",
    )
    global_args.add_argument(
        "-a",
        "--stat_analysis",
        action=argparse.BooleanOptionalAction,
        help="Run the RaP statistical analysis on the input file "
        f"[Default: {config.Config.DEFAULT_STATISTICAL_ANALYSIS}].",
    )
    global_args.add_argument(
        "-e",
        "--min_entropy",
        action=argparse.BooleanOptionalAction,
        help="Run the min-entropy calculation on the input file "
        f"[Default: {config.Config.DEFAULT_MINIMUM_ENTROPY}].",
    )
    global_args.add_argument(
        "--parallel",
        action=argparse.BooleanOptionalAction,
        help=f"Run the program in parallel mode [Default: {config.Config.DEFAULT_PARALLEL}].",
    )
    global_args.add_argument(
        "-d",
        "--debug",
        action=argparse.BooleanOptionalAction,
        help=f"Show debug messages [Default: {config.Config.DEFAULT_DEBUG}].",
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
        help=f"Number of symbols in the input sequence [Default: {config.Config.NISTConfig.DEFAULT_N_SYMBOLS}].",
    )
    nist_args.add_argument(
        "--nist_n_permutations",
        type=int,
        help="Number of permutations of the input sequence "
        f"[Default: {config.Config.NISTConfig.DEFAULT_N_PERMUTATIONS}].",
    )

    # Mutual exclusion between 'first_seq' and 'last_seq'
    first_seq_args = nist_args.add_mutually_exclusive_group()

    first_seq_args.add_argument(
        "--first_seq",
        default=None,
        action="store_true",
        help="Test the first sequence of [nist_n_symbols] symbols from the input file "
        f"[Default: {config.Config.NISTConfig.DEFAULT_FIRST_SEQ}].",
    )
    first_seq_args.add_argument(
        "--last_seq",
        default=None,
        action="store_false",
        dest="first_seq",
        help="Test the last sequence of [nist_n_symbols] symbols from the input file "
        f"[Default: {not config.Config.NISTConfig.DEFAULT_FIRST_SEQ}].",
    )
    nist_args.add_argument(
        "--plot",
        action=argparse.BooleanOptionalAction,
        help=(
            "Generate a histogram plot for each of the executed tests "
            f"[Default: {config.Config.NISTConfig.DEFAULT_PLOT}]."
        ),
    )
    nist_args.add_argument(
        "--nist_p",
        metavar="P",
        nargs="+",
        type=int,
        help=(
            "Lag parameters p used for periodicity and covariance tests "
            f"[Default: {config.Config.NISTConfig.DEFAULT_P}]"
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
        "--stat_n_symbols",
        type=int,
        help=f"Number of symbols in a sequence [Default: {config.Config.StatConfig.DEFAULT_N_SYMBOLS}].",
    )
    stat_args.add_argument(
        "--stat_n_permutations",
        type=int,
        help=f"Number of permutations [Default: {config.Config.StatConfig.DEFAULT_N_PERMUTATIONS}].",
    )
    stat_args.add_argument(
        "--stat_n_iterations",
        type=int,
        help=(
            "Number of iterations of the IID test suite to obtain the statistical distribution of counter C0 "
            f"[Default: {config.Config.StatConfig.DEFAULT_N_ITERATIONS}]."
        ),
    )
    stat_args.add_argument(
        "--stat_p",
        metavar="P",
        type=int,
        help="Single lag parameter p used for periodicity and covariance tests "
        f"[Default: {config.Config.StatConfig.DEFAULT_P}]",
    )

    args = parser.parse_args()
    try:
        conf = config.Config(args)
    except ValueError as e:
        logger.error(e)
        return ReturnValue.BAD_CONFIG

    rv = ReturnValue.OK
    # Create results folder and move into it
    current_run_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = Path(conf.input_file).stem  # Extracts the file name from the full path
    dir_name = f"{file_name}@{current_run_date}"
    results_dir = os.path.join("iid_results", dir_name)
    os.makedirs(results_dir, exist_ok=True)
    with contextlib.chdir(results_dir):
        # Configure logging
        # Write all loggers to file, each with their own level, from DEBUG up
        f_handler = logging.FileHandler(f"{dir_name}.log", mode="w")
        f_handler.setLevel(logging.DEBUG)
        f_handler.setFormatter(logging.Formatter("%(asctime)s %(name)-28s %(levelname)-8s %(message)s"))
        logger.addHandler(f_handler)

        # Write the application-specific logger to stderr, from INFO up
        s_handler = logging.StreamHandler()
        if conf.debug:
            s_handler.setLevel(logging.DEBUG)
        else:
            s_handler.setLevel(logging.INFO)
        s_handler.setFormatter(logging.Formatter("[%(relativeCreated)d] %(name)s: %(levelname)s: %(message)s"))
        logger.addHandler(s_handler)

        # Set application-specific logger level from DEBUG up
        logger.setLevel(logging.DEBUG)

        np.set_printoptions(suppress=True, threshold=np.inf, linewidth=np.inf, formatter={"float": "{:0.6f}".format})

        # Save configuration parameters in the results folder
        conf.to_json_file("configuration.json")
        logger.debug(conf.dump())

        if conf.nist_test:
            os.makedirs("IID_validation", exist_ok=True)
            with contextlib.chdir("IID_validation"):
                try:
                    iid_test.iid_test_function(conf)
                except Exception as e:
                    logger.error("NIST TEST failed: %s", e)
                    rv = ReturnValue.FAILED_ANALYSIS
        if conf.statistical_analysis:
            os.makedirs("statistical_analysis", exist_ok=True)
            with contextlib.chdir("statistical_analysis"):
                try:
                    statistical_analysis.statistical_analysis_function(conf)
                except Exception as e:
                    logger.error("Statistical analysis failed: %s", e)
                    rv = ReturnValue.FAILED_ANALYSIS
        if conf.min_entropy:
            os.makedirs("min_entropy", exist_ok=True)
            with contextlib.chdir("min_entropy"):
                try:
                    min_entropy.min_entropy_function(conf)
                except Exception as e:
                    logger.error("Min-entropy failed: %s", e)
                    rv = ReturnValue.FAILED_ANALYSIS
    return rv


# Configure application logger
logger = logging.getLogger("IID_validation")

if __name__ == "__main__":
    sys.exit(main())
