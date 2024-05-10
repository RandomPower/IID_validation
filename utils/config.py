import argparse
import logging
import os
import pathlib
import tomllib

import permutation_tests

# Configure per-module logger
logger = logging.getLogger(f"IID_validation.{pathlib.Path(__file__).stem}")


class Config:
    DEFAULT_CONFIG_FILE = "conf.toml"
    DEFAULT_NIST_TEST = True
    DEFAULT_STATISTICAL_ANALYSIS = False

    class NISTConfig:
        DEFAULT_SELECTED_TESTS = [i.id for i in permutation_tests.tests]
        DEFAULT_N_SYMBOLS = 1000000
        DEFAULT_N_PERMUTATIONS = 10000
        DEFAULT_FIRST_SEQ = True
        DEFAULT_PLOT = False
        # Default NIST values for lag parameter p
        DEFAULT_P = [1, 2, 8, 16, 32]

        def __init__(self) -> None:
            self._set_defaults()

        def _set_defaults(self) -> None:
            """Initialise member variables to default values."""
            self._selected_tests = self.DEFAULT_SELECTED_TESTS
            self._n_symbols = self.DEFAULT_N_SYMBOLS
            self._n_permutations = self.DEFAULT_N_PERMUTATIONS
            self._first_seq = self.DEFAULT_FIRST_SEQ
            self._plot = self.DEFAULT_PLOT
            self._p = self.DEFAULT_P

        @property
        def selected_tests(self):
            return self._selected_tests

        @property
        def n_symbols(self):
            return self._n_symbols

        @property
        def n_permutations(self):
            return self._n_permutations

        @property
        def first_seq(self):
            return self._first_seq

        @property
        def plot(self):
            return self._plot

        @property
        def p(self):
            return self._p

    class StatConfig:
        DEFAULT_SELECTED_TESTS = [i.id for i in permutation_tests.tests]
        DEFAULT_N_SYMBOLS = 1000
        DEFAULT_N_SEQUENCES = 200
        DEFAULT_N_ITERATIONS = 500
        DEFAULT_P = 2

        def __init__(self) -> None:
            self._set_defaults()

        def _set_defaults(self) -> None:
            """Initialise member variables to default values."""
            self._selected_tests = self.DEFAULT_SELECTED_TESTS
            self._n_sequences = self.DEFAULT_N_SEQUENCES
            self._n_symbols = self.DEFAULT_N_SYMBOLS
            self._n_iterations = self.DEFAULT_N_ITERATIONS
            self._p = self.DEFAULT_P

        @property
        def selected_tests(self):
            return self._selected_tests

        @property
        def n_sequences(self):
            return self._n_sequences

        @property
        def n_symbols(self):
            return self._n_symbols

        @property
        def n_iterations(self):
            return self._n_iterations

        @property
        def p(self):
            return self._p

    def __init__(self, args: argparse.Namespace) -> None:
        self._set_defaults()

        self._nist = Config.NISTConfig()
        self._stat = Config.StatConfig()

        # Read a user-provided configuration file, if specified
        if args.config:
            self._read_conf(args.config)
        else:
            self._read_conf(self.DEFAULT_CONFIG_FILE)

        self._parse_args(args)

        self._validate()

    def _set_defaults(self) -> None:
        """Initialise member variables to default values."""
        self._nist_test = self.DEFAULT_NIST_TEST
        self._statistical_analysis = self.DEFAULT_STATISTICAL_ANALYSIS

    def _read_conf(self, filename: str) -> None:
        """Read configuration file and set the parameters.

        Args:
            filename (str): the configuration file.
        """
        conf = parse_config_file(filename)

        # Global section
        if "global" in conf:
            if "input_file" in conf["global"]:
                self._input_file = os.path.abspath(os.path.expanduser(conf["global"]["input_file"]))
                if (not isinstance(self._input_file, str)) or (
                    not self._input_file.endswith((".bin", ".BIN", ".dat", ".DAT"))
                ):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        filename,
                        "global",
                        "input_file",
                        "binary file",
                    )
                if not os.path.isfile(self._input_file):
                    logger.error("%s: %s is not a valid file: %s", filename, "input_file", self._input_file)

            if "nist_test" in conf["global"]:
                self._nist_test = conf["global"]["nist_test"]
                if not isinstance(self._nist_test, bool):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        filename,
                        "global",
                        "nist_test",
                        "bool",
                    )

            if "stat_analysis" in conf["global"]:
                self._statistical_analysis = conf["global"]["stat_analysis"]
                if not isinstance(self._statistical_analysis, bool):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        filename,
                        "global",
                        "stat_analysis",
                        "bool",
                    )

        # nist_test section
        if "nist_test" in conf:
            if "selected_tests" in conf["nist_test"]:
                self.nist._selected_tests = conf["nist_test"]["selected_tests"]
                if (not isinstance(self.nist._selected_tests, list)) or (
                    not all(isinstance(i, int) for i in self.nist._selected_tests)
                ):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        filename,
                        "nist_test",
                        "selected_tests",
                        "list of integers",
                    )

            if "n_symbols" in conf["nist_test"]:
                self.nist._n_symbols = conf["nist_test"]["n_symbols"]
                if not isinstance(self.nist._n_symbols, int):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        filename,
                        "nist_test",
                        "n_symbols",
                        "int",
                    )

            if "n_permutations" in conf["nist_test"]:
                self.nist._n_permutations = conf["nist_test"]["n_permutations"]
                if not isinstance(self.nist._n_permutations, int):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        filename,
                        "nist_test",
                        "n_permutations",
                        "int",
                    )

            if "first_seq" in conf["nist_test"]:
                self.nist._first_seq = conf["nist_test"]["first_seq"]
                if not isinstance(self.nist._first_seq, bool):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        filename,
                        "nist_test",
                        "first_seq",
                        "bool",
                    )

            if "plot" in conf["nist_test"]:
                self.nist._plot = conf["nist_test"]["plot"]
                if not isinstance(self.nist._plot, bool):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        filename,
                        "nist_test",
                        "plot",
                        "bool",
                    )

            if "p" in conf["nist_test"]:
                self.nist._p = conf["nist_test"]["p"]
                if (not isinstance(self.nist._p, list)) or (not all(isinstance(i, int) for i in self.nist._p)):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        filename,
                        "nist_test",
                        "p",
                        "list of integers",
                    )

        # statistical_analysis section
        if "statistical_analysis" in conf:
            if "selected_tests" in conf["statistical_analysis"]:
                self.stat._selected_tests = conf["statistical_analysis"]["selected_tests"]
                if (not isinstance(self.stat._selected_tests, list)) or (
                    not all(isinstance(i, int) for i in self.stat._selected_tests)
                ):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        filename,
                        "statistical_analysis",
                        "selected_tests",
                        "list of integers",
                    )

            if "n_sequences" in conf["statistical_analysis"]:
                self.stat._n_sequences = conf["statistical_analysis"]["n_sequences"]
                if not isinstance(self.stat._n_sequences, int):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        filename,
                        "statistical_analysis",
                        "n_sequences",
                        "int",
                    )

            if "n_symbols" in conf["statistical_analysis"]:
                self.stat._n_symbols = conf["statistical_analysis"]["n_symbols"]
                if not isinstance(self.stat._n_symbols, int):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        filename,
                        "statistical_analysis",
                        "n_symbols",
                        "int",
                    )

            if "n_iterations" in conf["statistical_analysis"]:
                self.stat._n_iterations = conf["statistical_analysis"]["n_iterations"]
                if not isinstance(self.stat._n_iterations, int):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        filename,
                        "statistical_analysis",
                        "n_iterations",
                        "int",
                    )

            if "p" in conf["statistical_analysis"]:
                self.stat._p = conf["statistical_analysis"]["p"]
                if not isinstance(self.stat._p, int):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        filename,
                        "statistical_analysis",
                        "p",
                        "int",
                    )

    def _parse_args(self, args: argparse.Namespace) -> None:
        """Parse the command-line arguments.

        Args: args (argparse.Namespace): the list of arguments.
        """
        # Global
        if args.input_file:
            self._input_file = os.path.abspath(os.path.expanduser(args.input_file))
        if args.nist_test:
            self._nist_test = args.nist_test
        if args.stat_analysis:
            self._statistical_analysis = args.stat_analysis
        # NIST IID tests
        if args.nist_selected_tests:
            self.nist._selected_tests = args.nist_selected_tests
        if args.nist_n_symbols:
            self.nist._n_symbols = args.nist_n_symbols
        if args.nist_n_permutations:
            self.nist._n_permutations = args.nist_n_permutations
        if args.first_seq:
            self.nist._first_seq = args.first_seq
        if args.plot:
            self.nist._plot = args.plot
        if args.nist_p:
            self.nist._p = args.nist_p
        # Statistical analysis
        if args.stat_selected_tests:
            self.stat._selected_tests = args.stat_selected_tests
        if args.stat_n_sequences:
            self.stat._n_sequences = args.stat_n_sequences
        if args.stat_n_symbols:
            self.stat._n_symbols = args.stat_n_symbols
        if args.stat_n_iterations:
            self.stat._n_iterations = args.stat_n_iterations
        if args.stat_p:
            self.stat._p = args.stat_p

    def _validate(self) -> None:
        """Validate parameters.

        Check that required parameters are present.
        Check type and sanity of parameter values."""
        # Global
        # An input file is required
        if (
            (not self._input_file)
            or (not self._input_file.endswith((".bin", ".BIN", ".dat", ".DAT")))
            or (not os.path.isfile(self._input_file))
        ):
            raise ValueError(f'Invalid or missing configuration parameter: "input_file" ({self._input_file})')

        if not isinstance(self._nist_test, bool):
            raise ValueError(f'Invalid configuration parameter: "nist_test" ({self._nist_test})')

        if not isinstance(self._statistical_analysis, bool):
            raise ValueError(f'Invalid configuration parameter: "stat_analysis" ({self._statistical_analysis})')

        # NIST IID tests
        if (not self.nist._selected_tests) or (not isinstance(self.nist._selected_tests, list)):
            raise ValueError(f'Invalid configuration parameter: "nist_selected_tests" ({self.nist._selected_tests})')

        if (not self.nist._n_symbols) or (not isinstance(self.nist._n_symbols, int)):
            raise ValueError(f'Invalid configuration parameter: "nist_n_symbols" ({self.nist._n_symbols})')

        if (not self.nist._n_permutations) or (not isinstance(self.nist._n_permutations, int)):
            raise ValueError(f'Invalid configuration parameter: "nist_n_permutations" ({self.nist._n_permutations})')

        if not isinstance(self.nist._first_seq, bool):
            raise ValueError(f'Invalid configuration parameter: "first_seq" ({self.nist._first_seq})')

        if not isinstance(self.nist._plot, bool):
            raise ValueError(f'Invalid configuration parameter: "plot" ({self.nist._plot})')

        if (not self.nist._p) or (not isinstance(self.nist._p, list)):
            raise ValueError(f'Invalid configuration parameter: "nist_p" ({self.nist._p})')

        # Statistical analysis
        if (not self.stat._selected_tests) or (not isinstance(self.stat._selected_tests, list)):
            raise ValueError(f'Invalid configuration parameter: "stat_selected_tests" ({self.stat._selected_tests})')

        if (not self.stat._n_sequences) or (not isinstance(self.stat._n_sequences, int)):
            raise ValueError(f'Invalid configuration parameter: "stat_n_sequences" ({self.stat._n_sequences})')

        if (not self.stat._n_symbols) or (not isinstance(self.stat._n_symbols, int)):
            raise ValueError(f'Invalid configuration parameter: "stat_n_symbols" ({self.stat._n_symbols})')

        if (not self.stat._n_iterations) or (not isinstance(self.stat._n_iterations, int)):
            raise ValueError(f'Invalid configuration parameter: "n_iterations" ({self.stat._n_iterations})')

        if (not self.stat._p) or (not isinstance(self.stat._p, int)):
            raise ValueError(f'Invalid configuration parameter: "stat_p" ({self.stat._p})')

    @property
    def nist(self):
        return self._nist

    @property
    def stat(self):
        return self._stat

    @property
    def input_file(self):
        return self._input_file

    @property
    def nist_test(self):
        return self._nist_test

    @property
    def statistical_analysis(self):
        return self._statistical_analysis


def parse_config_file(file_path: str) -> dict:
    """Parse the specified file into a Python dictionary

    Args:
        file_path (str): the path of the configuration file.

    Returns:
        dict: a dictionary containing all the configuration values,
            or an empty dictionary if the configuration file cannot
            be parsed.
    """
    try:
        with open(file_path, "rb") as f:
            config_data: dict = tomllib.load(f)
        return config_data
    except IOError as e:
        logger.error("Unable to open or read config file: %s", e)
        return {}
    except Exception as e:
        logger.error("Unable to parse config file: %s", e)
        return {}


def file_info(conf: Config):
    f = open(conf.input_file, "rb")
    f.seek(0, 2)
    size = f.tell()
    logger.debug("FILE INFO")
    logger.debug("Input file: %s", conf.input_file)
    logger.debug("Size of file is: %s bytes", size)
    logger.debug("Number of symbols per sequence for counters analysis: %s", conf.stat.n_symbols)
    logger.debug("Number of sequences wanted for counters analysis: %s", conf.stat.n_sequences)
    # total number of symbols in the file
    max_symbols = size * 2
    max_sequences = max_symbols / conf.stat.n_symbols
    logger.debug("Maximum sequences that can be generated from the file: %s", max_sequences)
    tot_seqs = conf.stat._n_iterations * conf.stat.n_sequences
    logger.debug("Total sequences necessary = %s", tot_seqs)
    logger.debug("----------------------------------------------------------------\n")


def config_info(conf: Config):
    logger.debug("CONFIG INFO - NIST")
    logger.debug("Number of symbols per sequence = %s", conf.nist.n_symbols)
    logger.debug("Number of shuffled sequences = %s", conf.nist.n_permutations)
    ts = [permutation_tests.tests[i].name for i in conf.nist.selected_tests]
    logger.debug("Tests for entropy validation selected: %s", ts)
    if conf.nist.first_seq:
        logger.debug("Reference sequence read from the beginning of the file")
    else:
        logger.debug("Reference sequence read from the end of the file")
    if conf.nist.p == conf.nist.DEFAULT_P:
        logger.debug("p parameter used: NIST")
    else:
        logger.debug("p parameter used: user value")

    logger.debug("\nCONFIG INFO - STATISTICAL ANALYSIS")
    logger.debug("Number of symbols per sequence = %s", conf.stat.n_symbols)
    logger.debug("Number of shuffled sequences = %s", conf.stat.n_sequences)
    logger.debug("Number of iterations for counter: %s", conf.stat.n_iterations)
    stat_tests = [permutation_tests.tests[i].name for i in conf.stat.selected_tests]
    logger.debug("Test selected for counter distribution analysis: %s", stat_tests)
    logger.debug("p parameter used: user value: %s", conf.stat.p)
    logger.debug("----------------------------------------------------------------\n \nMAIN")
