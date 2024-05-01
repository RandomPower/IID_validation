import argparse
import logging
import pathlib
import tomllib
import os

import permutation_tests

# Configure per-module logger
logger = logging.getLogger(f"IID_validation.{pathlib.Path(__file__).stem}")


class Config:
    DEFAULT_CONFIG_FILE = "conf.toml"
    DEFAULT_NIST_TEST = True
    DEFAULT_STATISTICAL_ANALYSIS = False

    class NISTConfig:
        DEFAULT_SELECTED_TESTS = [i.id for i in permutation_tests.tests]
        DEFAULT_N_SYMBOLS = 100
        DEFAULT_N_SEQUENCES = 100000
        DEFAULT_SHUFFLE = True
        DEFAULT_FIRST_SEQ = True
        DEFAULT_SEE_PLOTS = False
        DEFAULT_PVALUES = [1, 2, 8, 16, 32]

        def __init__(self) -> None:
            self._set_defaults()

        def _set_defaults(self) -> None:
            """Initialise member variables to default values."""
            self._selected_tests = self.DEFAULT_SELECTED_TESTS
            self._n_symbols = self.DEFAULT_N_SYMBOLS
            self._n_sequences = self.DEFAULT_N_SEQUENCES
            self._shuffle = self.DEFAULT_SHUFFLE
            self._first_seq = self.DEFAULT_FIRST_SEQ
            self._plot = self.DEFAULT_SEE_PLOTS
            self._pvalues = self.DEFAULT_PVALUES

        @property
        def selected_tests(self):
            return self._selected_tests

        @property
        def n_symbols(self):
            return self._n_symbols

        @property
        def n_sequences(self):
            return self._n_sequences

        @property
        def shuffle(self):
            return self._shuffle

        @property
        def first_seq(self):
            return self._first_seq

        @property
        def plot(self):
            return self._plot

        @property
        def pvalues(self):
            return self._pvalues

    class StatConfig:
        DEFAULT_N_SYMBOLS = 1000
        DEFAULT_N_SEQUENCES = 200
        DEFAULT_N_ITERATIONS_C = 500
        DEFAULT_DISTRIBUTION_TEST_INDEX = 6
        DEFAULT_SHUFFLE = True
        DEFAULT_P_VALUE = 2
        DEFAULT_REF_NUMBERS = [1, 3, 4]

        def __init__(self) -> None:
            self._set_defaults()

        def _set_defaults(self) -> None:
            """Initialise member variables to default values."""
            self._n_sequences = self.DEFAULT_N_SEQUENCES
            self._n_symbols = self.DEFAULT_N_SYMBOLS
            self._n_iterations_c = self.DEFAULT_N_ITERATIONS_C
            self._distribution_test_index = self.DEFAULT_DISTRIBUTION_TEST_INDEX
            self._shuffle = self.DEFAULT_SHUFFLE
            self._p_value = self.DEFAULT_P_VALUE
            self._ref_numbers = self.DEFAULT_REF_NUMBERS

        @property
        def n_sequences(self):
            return self._n_sequences

        @property
        def n_symbols(self):
            return self._n_symbols

        @property
        def n_iterations_c(self):
            return self._n_iterations_c

        @property
        def distribution_test_index(self):
            return self._distribution_test_index

        @property
        def shuffle(self):
            return self._shuffle

        @property
        def p_value(self):
            return self._p_value

        @property
        def ref_numbers(self):
            return self._ref_numbers

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
                        "%s: invalid configuration parameter %s (expected %s)", filename, "input_file", "binary file"
                    )
                if not os.path.isfile(self._input_file):
                    logger.error("%s: %s is not a valid file: %s", filename, "input_file", self._input_file)

            if "test_nist" in conf["global"]:
                self._nist_test = conf["global"]["test_nist"]
                if not isinstance(self._nist_test, bool):
                    logger.error("%s: invalid configuration parameter %s (expected %s)", filename, "test_nist", "bool")

            if "stat_analysis" in conf["global"]:
                self._statistical_analysis = conf["global"]["stat_analysis"]
                if not isinstance(self._statistical_analysis, bool):
                    logger.error(
                        "%s: invalid configuration parameter %s (expected %s)", filename, "stat_analysis", "bool"
                    )

        # nist_test section
        if "nist_test" in conf:
            if "selected_tests" in conf["nist_test"]:
                self.nist._selected_tests = conf["nist_test"]["selected_tests"]
                if (not isinstance(self.nist._selected_tests, list)) or (
                    not all(isinstance(i, int) for i in self.nist._selected_tests)
                ):
                    logger.error(
                        "%s: invalid configuration parameter %s (expected %s)",
                        filename,
                        "selected_tests",
                        "list of integers",
                    )

            if "n_symbols" in conf["nist_test"]:
                self.nist._n_symbols = conf["nist_test"]["n_symbols"]
                if not isinstance(self.nist._n_symbols, int):
                    logger.error("%s: invalid configuration parameter %s (expected %s)", filename, "n_symbols", "int")

            if "n_sequences" in conf["nist_test"]:
                self.nist._n_sequences = conf["nist_test"]["n_sequences"]
                if not isinstance(self.nist._n_sequences, int):
                    logger.error(
                        "%s: invalid configuration parameter %s (expected %s)", filename, "n_sequences", "int"
                    )

            if "shuffle" in conf["nist_test"]:
                self.nist._shuffle = conf["nist_test"]["shuffle"]
                if not isinstance(self.nist._shuffle, bool):
                    logger.error("%s: invalid configuration parameter %s (expected %s)", filename, "shuffle", "bool")

            if "first_seq" in conf["nist_test"]:
                self.nist._first_seq = conf["nist_test"]["first_seq"]
                if not isinstance(self.nist._first_seq, bool):
                    logger.error("%s: invalid configuration parameter %s (expected %s)", filename, "first_seq", "bool")

            if "plot" in conf["nist_test"]:
                self.nist._plot = conf["nist_test"]["plot"]
                if not isinstance(self.nist._plot, bool):
                    logger.error("%s: invalid configuration parameter %s (expected %s)", filename, "plot", "bool")

            if "p" in conf["nist_test"]:
                self.nist._pvalues = conf["nist_test"]["p"]
                if (not isinstance(self.nist._pvalues, list)) or (
                    not all(isinstance(i, int) for i in self.nist._pvalues)
                ):
                    logger.error(
                        "%s: invalid configuration parameter %s (expected %s)", filename, "p", "list of integers"
                    )

        # statistical_analysis section
        if "statistical_analysis" in conf:
            if "n_sequences" in conf["statistical_analysis"]:
                self.stat._n_sequences = conf["statistical_analysis"]["n_sequences"]
                if not isinstance(self.stat._n_sequences, int):
                    logger.error(
                        "%s: invalid configuration parameter %s (expected %s)", filename, "n_sequences", "int"
                    )

            if "n_symbols" in conf["statistical_analysis"]:
                self.stat._n_symbols = conf["statistical_analysis"]["n_symbols"]
                if not isinstance(self.stat._n_symbols, int):
                    logger.error("%s: invalid configuration parameter %s (expected %s)", filename, "n_symbols", "int")

            if "n_iterations_c" in conf["statistical_analysis"]:
                self.stat._n_iterations_c = conf["statistical_analysis"]["n_iterations_c"]
                if not isinstance(self.stat.n_iterations_c, int):
                    logger.error(
                        "%s: invalid configuration parameter %s (expected %s)", filename, "n_iterations_c", "int"
                    )

            if "distribution_test_index" in conf["statistical_analysis"]:
                self.stat._distribution_test_index = conf["statistical_analysis"]["distribution_test_index"]
                if not isinstance(self.stat._distribution_test_index, int):
                    logger.error(
                        "%s: invalid configuration parameter %s (expected %s)",
                        filename,
                        "distribution_test_index",
                        "int",
                    )

            if "shuffle" in conf["statistical_analysis"]:
                self.stat._shuffle = conf["statistical_analysis"]["shuffle"]
                if not isinstance(self.stat._shuffle, bool):
                    logger.error("%s: invalid configuration parameter %s (expected %s)", filename, "shuffle", "bool")

            if "p_value" in conf["statistical_analysis"]:
                self.stat._p_value = conf["statistical_analysis"]["p_value"]
                if not isinstance(self.stat._p_value, int):
                    logger.error("%s: invalid configuration parameter %s (expected %s)", filename, "p_value", "int")

            if "ref_numbers" in conf["statistical_analysis"]:
                self.stat._ref_numbers = conf["statistical_analysis"]["ref_numbers"]
                if not isinstance(self.stat._ref_numbers, list):
                    logger.error(
                        "%s: invalid configuration parameter %s (expected %s)", filename, "ref_numbers", "list"
                    )

    def _parse_args(self, args: argparse.Namespace) -> None:
        """Parse the command-line arguments.

        Args: args (argparse.Namespace): the list of arguments.
        """
        # Global
        if args.input_file:
            self._input_file = os.path.abspath(os.path.expanduser(args.input_file))
        if args.test_nist:
            self._nist_test = args.test_nist
        if args.stat_analysis:
            self._statistical_analysis = args.stat_analysis
        # NIST IID tests
        if args.nist_selected_tests:
            self.nist._selected_tests = args.nist_selected_tests
        if args.nist_n_symbols:
            self.nist._n_symbols = args.nist_n_symbols
        if args.nist_n_sequences:
            self.nist._n_sequences = args.nist_n_sequences
        if args.shuffle:
            self.nist._shuffle = args.shuffle
        if args.first_seq:
            self.nist._first_seq = args.first_seq
        if args.plot:
            self.nist._plot = args.plot
        if args.pvalues:
            self.nist._pvalues = args.pvalues
        # Statistical analysis
        if args.stat_n_sequences:
            self.stat._n_sequences = args.stat_n_sequences
        if args.stat_n_symbols:
            self.stat._n_symbols = args.stat_n_symbols
        if args.stat_n_iter_c:
            self.stat._n_iterations_c = args.stat_n_iter_c
        if args.distr_test_idx:
            self.stat._distribution_test_index = args.distr_test_idx
        if args.stat_shuffle:
            self.stat._shuffle = args.stat_shuffle
        if args.stat_pvalue:
            self.stat._p_value = args.stat_pvalue
        if args.ref_nums:
            self.stat._ref_numbers = args.ref_nums

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
            raise ValueError(f'Invalid configuration parameter: "test_nist" ({self._nist_test})')

        if not isinstance(self._statistical_analysis, bool):
            raise ValueError(f'Invalid configuration parameter: "stat_analysis" ({self._statistical_analysis})')

        # NIST IID tests
        if (not self.nist._selected_tests) or (not isinstance(self.nist._selected_tests, list)):
            raise ValueError(f'Invalid configuration parameter: "nist_selected_tests" ({self.nist._selected_tests})')

        if (not self.nist._n_symbols) or (not isinstance(self.nist._n_symbols, int)):
            raise ValueError(f'Invalid configuration parameter: "n_symbols" ({self.nist._n_symbols})')

        if (not self.nist._n_sequences) or (not isinstance(self.nist._n_sequences, int)):
            raise ValueError(f'Invalid configuration parameter: "n_sequences" ({self.nist._n_sequences})')

        if not isinstance(self.nist._shuffle, bool):
            raise ValueError(f'Invalid configuration parameter: "shuffle" ({self.nist._shuffle})')

        if not isinstance(self.nist._first_seq, bool):
            raise ValueError(f'Invalid configuration parameter: "first_seq" ({self.nist._first_seq})')

        if not isinstance(self.nist._plot, bool):
            raise ValueError(f'Invalid configuration parameter: "plot" ({self.nist._plot})')

        if (not self.nist._pvalues) or (not isinstance(self.nist._pvalues, list)):
            raise ValueError(f'Invalid configuration parameter: "pvalues" ({self.nist._pvalues})')

        # Statistical analysis
        if (not self.stat._n_sequences) or (not isinstance(self.stat._n_sequences, int)):
            raise ValueError(f'Invalid configuration parameter: "stat_n_sequences" ({self.stat._n_sequences})')

        if (not self.stat._n_symbols) or (not isinstance(self.stat._n_symbols, int)):
            raise ValueError(f'Invalid configuration parameter: "stat_n_symbols" ({self.stat._n_symbols})')

        if (not self.stat._n_iterations_c) or (not isinstance(self.stat._n_iterations_c, int)):
            raise ValueError(f'Invalid configuration parameter: "stat_n_iter_c" ({self.stat._n_iterations_c})')

        if (not self.stat._distribution_test_index) or (not isinstance(self.stat._distribution_test_index, int)):
            raise ValueError(
                f'Invalid configuration parameter: "distr_test_idx" ({self.stat._distribution_test_index})'
            )

        if not isinstance(self.stat._shuffle, bool):
            raise ValueError(f'Invalid configuration parameter: "shuffle" ({self.stat._shuffle})')

        if (not self.stat._p_value) or (not isinstance(self.stat._p_value, int)):
            raise ValueError(f'Invalid configuration parameter: "stat_pvalue" ({self.stat._p_value})')

        if (not self.stat._ref_numbers) or (not isinstance(self.stat._ref_numbers, list)):
            raise ValueError(f'Invalid configuration parameter: "ref_nums" ({self.stat._ref_numbers})')

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
    tot_seqs = conf.stat.n_iterations_c * conf.stat.n_sequences
    logger.debug("Total sequences necessary = %s", tot_seqs)
    if not conf.stat.shuffle:
        if tot_seqs <= max_sequences:
            logger.debug("SHUFFLE FROM FILE ALLOWED WITH THIS FILE")
        else:
            logger.error("SHUFFLE FROM FILE NOT ALLOWED WITH THIS FILE")
            raise Exception(
                f"Insufficient sequences (provided {max_sequences}, required {tot_seqs}) in {conf.input_file}"
            )
    logger.debug("----------------------------------------------------------------\n")


def config_info(conf: Config):
    logger.debug("CONFIG INFO - NIST")
    logger.debug("Number of symbols per sequence = %s", conf.nist.n_symbols)
    logger.debug("Number of shuffled sequences = %s", conf.nist.n_sequences)
    ts = [permutation_tests.tests[i].name for i in conf.nist.selected_tests]
    logger.debug("Tests for entropy validation selected: %s", ts)
    if conf.nist.first_seq:
        logger.debug("Reference sequence read from the beginning of the file")
    else:
        logger.debug("Reference sequence read from the end of the file")
    if conf.nist.pvalues == conf.nist.DEFAULT_PVALUES:
        logger.debug("p parameter used: NIST")
    else:
        logger.debug("p parameter used: user value")

    logger.debug("\nCONFIG INFO - STATISTICAL ANALYSIS")
    logger.debug("Number of symbols per sequence = %s", conf.stat.n_symbols)
    logger.debug("Number of shuffled sequences = %s", conf.stat.n_sequences)
    logger.debug("Number of iterations for counter: %s", conf.stat.n_iterations_c)
    logger.debug(
        "Test selected for counter distribution analysis: %s",
        permutation_tests.tests[conf.stat.distribution_test_index].name,
    )
    comp = [permutation_tests.tests[i].name for i in conf.stat.ref_numbers]
    logger.debug("Tests selected test for shuffle/random comparison: %s", comp)
    logger.debug("p parameter used: user value: %s", conf.stat.p_value)
    logger.debug("----------------------------------------------------------------\n \nMAIN")
