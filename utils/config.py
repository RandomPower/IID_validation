"""
CONFIGURATION FILE - CHANGE VARIABLES TO RUN THE DESIRED CONFIGURATION
"""

import argparse
import logging
import tomllib

import permutation_tests


class Config:
    DEFAULT_CONFIG_FILE = "conf.toml"
    DEFAULT_NIST_TEST = True
    DEFAULT_STATISTICAL_ANALYSIS = False
    DEFAULT_TEST_LIST_INDEXES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    DEFAULT_N_SEQUENCES = 100000
    DEFAULT_N_SYMBOLS = 100
    DEFAULT_SHUFFLE_NIST = True
    DEFAULT_FIRST_SEQ = True
    DEFAULT_SEE_PLOTS = False
    DEFAULT_NIST_PVALUES = [1, 2, 8, 16, 32]

    DEFAULT_N_SEQUENCES_STAT = 200
    DEFAULT_N_SYMBOLS_STAT = 1000
    DEFAULT_N_ITERATIONS_C_STAT = 500
    DEAULT_DISTRIBUTION_TEST_INDEX = 6
    DEFAULT_SHUFFLE_STAT = True
    DEFAULT_P_VALUE_STAT = 2
    DEFAULT_REF_NUMBERS = [1, 3, 4]

    def __init__(self, args: argparse.Namespace) -> None:
        self._set_defaults()

        # Verify whether the user has specified a configuration file.
        if args.config:
            self._read_conf(args.config)
        else:
            self._read_conf(self.DEFAULT_CONFIG_FILE)

        self._parse_args(args)

        self._validate()

    def _set_defaults(self) -> None:
        """ Set the default parameter values
        """
        self._nist_test = self.DEFAULT_NIST_TEST
        self._statistical_analysis = self.DEFAULT_STATISTICAL_ANALYSIS
        self._test_list_indexes = self.DEFAULT_TEST_LIST_INDEXES

        self._n_symbols = self.DEFAULT_N_SYMBOLS
        self._n_sequences = self.DEFAULT_N_SEQUENCES
        self._shuffle_nist = self.DEFAULT_SHUFFLE_NIST
        self._first_seq = self.DEFAULT_FIRST_SEQ
        self._see_plots = self.DEFAULT_SEE_PLOTS
        self._nist_pvalues = self.DEFAULT_NIST_PVALUES

        self._n_sequences_stat = self.DEFAULT_N_SEQUENCES_STAT
        self._n_symbols_stat = self.DEFAULT_N_SYMBOLS_STAT
        self._n_iterations_c_stat = self.DEFAULT_N_ITERATIONS_C_STAT
        self._distribution_test_index = self.DEAULT_DISTRIBUTION_TEST_INDEX
        self._shuffle_stat = self.DEFAULT_SHUFFLE_STAT
        self._p_value_stat = self.DEFAULT_P_VALUE_STAT
        self._ref_numbers = self.DEFAULT_REF_NUMBERS

    def _read_conf(self, filename: str) -> None:
        """Read configuration file and set the parameters.

        Args:
            filename (str): the configuration file.
        """
        conf = parse_config_file(filename)

        if "global" in conf and "input_file" in conf["global"]:
            self._input_file = conf["global"]["input_file"]
            if (not isinstance(self._input_file, str)) or (
                not self._input_file.endswith((".bin", ".BIN", ".dat", ".DAT"))
            ):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "input_file", "binary file")

        if "global" in conf and "bool_test_nist" in conf["global"]:
            self._nist_test = conf["global"]["bool_test_nist"]
            if not isinstance(self._nist_test, bool):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "bool_test_nist", "bool")

        if "global" in conf and "bool_statistical_analysis" in conf["global"]:
            self._statistical_analysis = conf["global"]["bool_statistical_analysis"]
            if not isinstance(self._statistical_analysis, bool):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "bool_statistical_analysis", "bool")

        if "global" in conf and "test_list_indexes" in conf["global"]:
            self._test_list_indexes = conf["global"]["test_list_indexes"]
            if not isinstance(self._test_list_indexes, list):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "test_list_indexes", "list")

        if "nist_test" in conf and "n_symbols" in conf["nist_test"]:
            self._n_symbols = conf["nist_test"]["n_symbols"]
            if not isinstance(self._n_symbols, int):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "n_symbols", "int")

        if "nist_test" in conf and "n_sequences" in conf["nist_test"]:
            self._n_sequences = conf["nist_test"]["n_sequences"]
            if not isinstance(self._n_sequences, int):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "n_sequences", "int")

        if "nist_test" in conf and "bool_shuffle_NIST" in conf["nist_test"]:
            self._shuffle_nist = conf["nist_test"]["bool_shuffle_NIST"]
            if not isinstance(self._shuffle_nist, bool):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "bool_shuffle_NIST", "bool")

        if "nist_test" in conf and "bool_first_seq" in conf["nist_test"]:
            self._first_seq = conf["nist_test"]["bool_first_seq"]
            if not isinstance(self._first_seq, bool):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "bool_first_seq", "bool")


        if "nist_test" in conf and "see_plots" in conf["nist_test"]:
            self._see_plots = conf["nist_test"]["see_plots"]
            if not isinstance(self._see_plots, bool):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "see_plots", "bool")

        if "nist_test" in conf and "p" in conf["nist_test"]:
            self._nist_pvalues = conf["nist_test"]["p"]
            if not isinstance(self._nist_pvalues, list):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "p", "list")

        if "statistical_analysis" in conf and "n_sequences_stat" in conf["statistical_analysis"]:
            self._n_sequences_stat = conf["statistical_analysis"]["n_sequences_stat"]
            if not isinstance(self._n_sequences_stat, int):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "n_sequences_stat", "int")

        if "statistical_analysis" in conf and "n_symbols_stat" in conf["statistical_analysis"]:
            self._n_symbols_stat = conf["statistical_analysis"]["n_symbols_stat"]
            if not isinstance(self._n_symbols_stat, int):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "n_symbols_stat", "int")

        if "statistical_analysis" in conf and "n_iterations_c_stat" in conf["statistical_analysis"]:
            self._n_iterations_c_stat = conf["statistical_analysis"]["n_iterations_c_stat"]
            if not isinstance(self.n_iterations_c_stat, int):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "n_iterations_c_stat", "int")

        if "statistical_analysis" in conf and "distribution_test_index" in conf["statistical_analysis"]:
            self._distribution_test_index = conf["statistical_analysis"]["distribution_test_index"]
            if not isinstance(self._distribution_test_index, int):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "distribution_test_index", "int")

        if "statistical_analysis" in conf and "bool_shuffle_stat" in conf["statistical_analysis"]:
            self._shuffle_stat = conf["statistical_analysis"]["bool_shuffle_stat"]
            if not isinstance(self._shuffle_stat, bool):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "bool_shuffle_stat", "bool")

        if "statistical_analysis" in conf and "p_value_stat" in conf["statistical_analysis"]:
            self._p_value_stat = conf["statistical_analysis"]["p_value_stat"]
            if not isinstance(self._p_value_stat, int):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "p_value_stat", "int")

        if "statistical_analysis" in conf and "ref_numbers" in conf["statistical_analysis"]:
            self._ref_numbers = conf["statistical_analysis"]["ref_numbers"]
            if not isinstance(self._ref_numbers, list):
                logging.error("%s: invalid configuration parameter %s (expected %s)", filename, "ref_numbers", "list")

    def _parse_args(self, args: argparse.Namespace) -> None:
        """ Parse the command-line arguments.

        Args: args (argparse.Namespace): the list of arguments.
        """
        if args.input_file:
            self._input_file = args.input_file
        if args.test_nist:
            self._nist_test = args.test_nist
        if args.stat_analysis:
            self._statistical_analysis = args.stat_analysis
        if args.test_list_idx:
            self._test_list_indexes = args.test_list_idx
        if args.n_symbols:
            self._n_symbols = args.n_symbols
        if args.n_sequences:
            self._n_sequences = args.n_sequences
        if args.shuffle_nist:
            self._shuffle_nist = args.shuffle_nist
        if args.first_seq:
            self._first_seq = args.first_seq
        if args.pvalue:
            self._pvalue = args.pvalue
        if args.see_plots:
            self._see_plots = args.see_plots
        if args.nist_pvalues:
            self._nist_pvalues = args.nist_pvalues
        if args.n_seq_stat:
            self._n_sequences_stat = args.n_seq_stat
        if args.n_symb_stat:
            self._n_symbols_stat = args.n_symb_stat
        if args.n_iter_c_stat:
            self._n_iterations_c_stat = args.n_iter_c_stat
        if args.distr_test_idx:
            self._distribution_test_index = args.distr_test_idx
        if args.shuffle_stat:
            self._shuffle_stat = args.shuffle_stat
        if args.pvalue_stat:
            self._p_value_stat = args.pvalue_stat
        if args.ref_nums:
            self._ref_numbers = args.ref_nums

    def _validate(self) -> None:
        """ Verify the presence and validity of the required parameters.
        """
        # Verify the existence of an input file, and whether it is a raw binary file (.BIN or .DAT)
        if (not self._input_file) or (not self._input_file.endswith((".bin", ".BIN", ".dat", ".DAT"))):
            raise ValueError(f'Invalid or missing configuration parameter: "input_file" ({self._input_file})')

        if not isinstance(self._nist_test, bool):
            raise ValueError(f'Invalid configuration parameter: "test_nist" ({self._nist_test})')

        if not isinstance(self._statistical_analysis, bool):
            raise ValueError(f'Invalid configuration parameter: "stat_analysis" ({self._statistical_analysis})')

        if (not self._test_list_indexes) or (not isinstance(self._test_list_indexes, list)):
            raise ValueError(f'Invalid configuration parameter: "test_list_idx" ({self._test_list_indexes})')

        if (not self._n_symbols) or (not isinstance(self._n_symbols, int)):
            raise ValueError(f'Invalid configuration parameter: "n_symbols" ({self._n_symbols})')

        if (not self._n_sequences) or (not isinstance(self._n_sequences, int)):
            raise ValueError(f'Invalid configuration parameter: "n_sequences" ({self._n_sequences})')

        if not isinstance(self._shuffle_nist, bool):
            raise ValueError(f'Invalid configuration parameter: "shuffle_nist" ({self._shuffle_nist})')

        if not isinstance(self._first_seq, bool):
            raise ValueError(f'Invalid configuration parameter: "first_seq" ({self._first_seq})')

        if not isinstance(self._pvalue, bool):
            raise ValueError(f'Invalid configuration parameter: "pvalue" ({self._pvalue})')

        if not isinstance(self._see_plots, bool):
            raise ValueError(f'Invalid configuration parameter: "see_plots" ({self._see_plots})')

        if (not self._nist_pvalues) or (not isinstance(self._nist_pvalues, list)):
            raise ValueError(f'Invalid configuration parameter: "nist_pvalues" ({self._nist_pvalues})')

        if (not self._n_sequences_stat) or (not isinstance(self._n_sequences_stat, int)):
            raise ValueError(f'Invalid configuration parameter: "n_seq_stat" ({self._n_sequences_stat})')

        if (not self._n_symbols_stat) or (not isinstance(self._n_symbols_stat, int)):
            raise ValueError(f'Invalid configuration parameter: "n_symb_stat" ({self._n_symbols_stat})')

        if (not self._n_iterations_c_stat) or (not isinstance(self._n_iterations_c_stat, int)):
            raise ValueError(f'Invalid configuration parameter: "n_iter_c_stat" ({self._n_iterations_c_stat})')

        if (not self._distribution_test_index) or (not isinstance(self._distribution_test_index, int)):
            raise ValueError(f'Invalid configuration parameter: "distr_test_idx" ({self._distribution_test_index})')

        if not isinstance(self._shuffle_stat, bool):
            raise ValueError(f'Invalid configuration parameter: "shuffle_stat" ({self._shuffle_stat})')

        if (not self._p_value_stat) or (not isinstance(self._p_value_stat, int)):
            raise ValueError(f'Invalid configuration parameter: "pvalue_stat" ({self._p_value_stat})')

        if (not self._ref_numbers) or (not isinstance(self._ref_numbers, list)):
            raise ValueError(f'Invalid configuration parameter: "ref_nums" ({self._ref_numbers})')

    @property
    def input_file(self):
        return self._input_file

    @property
    def nist_test(self):
        return self._nist_test

    @property
    def statistical_analysis(self):
        return self._statistical_analysis

    @property
    def test_list_indexes(self):
        return self._test_list_indexes

    @property
    def n_symbols(self):
        return self._n_symbols

    @property
    def n_sequences(self):
        return self._n_sequences

    @property
    def shuffle_nist(self):
        return self._shuffle_nist

    @property
    def first_seq(self):
        return self._first_seq

    @property
    # TO MODIFY
    def pvalue(self):
        return self._pvalue

    @property
    def see_plots(self):
        return self._see_plots

    @property
    def nist_pvalues(self):
        return self._nist_pvalues

    @property
    def n_sequences_stat(self):
        return self._n_sequences_stat

    @property
    def n_symbols_stat(self):
        return self._n_symbols_stat

    @property
    def n_iterations_c_stat(self):
        return self._n_iterations_c_stat

    @property
    def distribution_test_index(self):
        return self._distribution_test_index

    @property
    def shuffle_stat(self):
        return self._shuffle_stat

    @property
    def p_value_stat(self):
        return self._p_value_stat

    @property
    def ref_numbers(self):
        return self._ref_numbers


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
        logging.error("Unable to open or read config file: %s", e)
        return {}
    except Exception as e:
        logging.error("Unable to parse config file: %s", e)
        return {}


def init_config_data(args):
    """ Initialize a Config object.
    """
    global config_data
    config_data = Config(args)


def update_config_data(args: argparse.Namespace) -> None:
    """ Update the configuration dictionary with the user-defined args.

    Args:
        args (argparse.Namespace): the namespace containing the parsed args. 
    """
    # Mandatory arguments
    config_data["global"]["input_file"] = args.input_file
    config_data["nist_test"]["n_symbols"] = args.n_symbols
    config_data["nist_test"]["n_sequences"] = args.n_sequences
    config_data["statistical_analysis"]["n_sequences_stat"] = args.n_seq_stat
    config_data["statistical_analysis"]["n_symbols_stat"] = args.n_symb_stat
    config_data["statistical_analysis"]["n_iterations_c_stat"] = args.n_iter_c_stat
    config_data["statistical_analysis"]["distribution_test_index"] = args.distr_test_idx
    config_data["statistical_analysis"]["p_value_stat"] = args.pvalue_stat

    # Optional arguments
    if args.test_nist is not None:
        config_data["global"]["bool_test_NIST"] = args.test_nist
    if args.stat_analysis is not None:
        config_data["global"]["bool_statistical_analysis"] = args.stat_analysis
    if args.shuffle_nist is not None:
        config_data["nist_test"]["bool_shuffle_NIST"] = args.shuffle_nist
    if args.first_seq is not None:
        config_data["nist_test"]["bool_first_seq"] = args.first_seq
    if args.pvalue is not None:
        config_data["nist_test"]["bool_pvalue"] = args.pvalue
    if args.see_plots is not None:
        config_data["nist_test"]["see_plots"] = args.see_plots
    if args.shuffle_stat is not None:
        config_data["statistical_analysis"]["bool_shuffle_stat"] = args.shuffle_stat
    if args.ref_nums is not None:
        config_data["statistical_analysis"]["ref_numbers"] = args.ref_nums


config_data = parse_config_file("conf.toml")

if config_data["nist_test"]["bool_pvalue"]:
    # NIST values
    p = [1, 2, 8, 16, 32]
else:
    # User sets preferred value
    p = [2]


def file_info():
    f = open(config_data["global"]["input_file"], "r+b")
    f.seek(0, 2)
    size = f.tell()
    logging.debug("FILE INFO")
    logging.debug("Size of file is: %s bytes", size)
    logging.debug(
        "Number of symbols per sequence for counters analysis: %s",
        config_data["statistical_analysis"]["n_symbols_stat"],
    )
    logging.debug(
        "Number of sequences wanted for counters analysis: %s", config_data["statistical_analysis"]["n_sequences_stat"]
    )
    # total number of symbols in the file
    max_symbols = size * 2
    max_sequences = max_symbols / config_data["statistical_analysis"]["n_symbols_stat"]
    logging.debug("Maximum sequences that can be generated from the file: %s", max_sequences)
    tot_seqs = (
        config_data["statistical_analysis"]["n_iterations_c_stat"]
        * config_data["statistical_analysis"]["n_sequences_stat"]
    )
    logging.debug("Total sequences necessary = %s", tot_seqs)
    if not config_data["statistical_analysis"]["bool_shuffle_stat"]:
        if tot_seqs <= max_sequences:
            logging.debug("SHUFFLE FROM FILE ALLOWED WITH THIS FILE")
        else:
            logging.error("SHUFFLE FROM FILE NOT ALLOWED WITH THIS FILE")
            raise Exception(
                f"Insufficient sequences (provided {max_sequences}, required {tot_seqs})"
                + f" in {config_data['global']['input_file']}"
            )
    logging.debug("----------------------------------------------------------------\n")


def config_info():
    logging.debug("CONFIG INFO - NIST")
    logging.debug("Number of symbols per sequence = %s", config_data["nist_test"]["n_symbols"])
    logging.debug("Number of shuffled sequences = %s", config_data["nist_test"]["n_sequences"])
    ts = [permutation_tests.tests[i].name for i in config_data["global"]["test_list_indexes"]]
    logging.debug("Tests for entropy validation selected: %s", ts)
    if config_data["nist_test"]["bool_first_seq"]:
        logging.debug("Reference sequence read from the beginning of the file")
    else:
        logging.debug("Reference sequence read from the end of the file")
    if p == [1, 2, 8, 16, 32]:
        logging.debug("p parameter used: NIST")
    else:
        logging.debug("p parameter used: user value")

    logging.debug("\nCONFIG INFO - STATISTICAL ANALYSIS")
    logging.debug("Number of symbols per sequence = %s", config_data["statistical_analysis"]["n_symbols_stat"])
    logging.debug("Number of shuffled sequences = %s", config_data["statistical_analysis"]["n_sequences_stat"])
    logging.debug("Number of iterations for counter: %s", config_data["statistical_analysis"]["n_iterations_c_stat"])
    logging.debug(
        "Test selected for counter distribution analysis: %s",
        permutation_tests.tests[config_data["statistical_analysis"]["distribution_test_index"]].name,
    )
    comp = [permutation_tests.tests[i].name for i in config_data["statistical_analysis"]["ref_numbers"]]
    logging.debug("Tests selected test for shuffle/random comparison: %s", comp)
    logging.debug("p parameter used: user value: %s", config_data["statistical_analysis"]["p_value_stat"])
    logging.debug("----------------------------------------------------------------\n \nMAIN")
