import argparse
import collections
import hashlib
import json
import logging
import os
import pathlib
import tomllib
import typing

from . import permutation_tests

# Configure per-module logger
logger = logging.getLogger(f"IID_validation.{pathlib.Path(__file__).stem}")


class Config:
    DEFAULT_HASH_ALGORITHM = "sha256"

    DEFAULT_CONFIG_FILE = "conf.toml"
    DEFAULT_SYMBOL_LENGTH = 4
    DEFAULT_ALPHABET_SIZE = 2**DEFAULT_SYMBOL_LENGTH
    DEFAULT_NIST_TEST = True
    DEFAULT_STATISTICAL_ANALYSIS = True
    DEFAULT_MINIMUM_ENTROPY = True
    DEFAULT_PARALLEL = True
    DEFAULT_DEBUG = False

    _input_file: str
    _input_file_digest: str
    _config_file: str
    _config_file_read: bool
    _nist_test: bool
    _statistical_analysis: bool
    _min_entropy: bool
    _parallel: bool
    _debug: bool

    class NISTConfig:
        DEFAULT_SELECTED_TESTS = [i.id for i in permutation_tests.tests]
        DEFAULT_N_SYMBOLS = 1000000
        DEFAULT_N_PERMUTATIONS = 10000
        DEFAULT_FIRST_SEQ = True
        DEFAULT_PLOT = True
        # Default NIST values for lag parameter p
        DEFAULT_P = [1, 2, 8, 16, 32]

        _selected_tests: list[int]
        _n_symbols: int
        _n_permutations: int
        _first_seq: bool
        _plot: bool
        _p: list[int]

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
        def selected_tests(self) -> list[int]:
            return self._selected_tests

        @property
        def n_symbols(self) -> int:
            return self._n_symbols

        @property
        def n_permutations(self) -> int:
            return self._n_permutations

        @property
        def first_seq(self) -> bool:
            return self._first_seq

        @property
        def plot(self) -> bool:
            return self._plot

        @property
        def p(self) -> list[int]:
            return self._p

    class StatConfig:
        DEFAULT_SELECTED_TESTS = [i.id for i in permutation_tests.tests]
        DEFAULT_N_SYMBOLS = 1000
        DEFAULT_N_PERMUTATIONS = 200
        DEFAULT_N_ITERATIONS = 500
        DEFAULT_P = 2

        _selected_tests: list[int]
        _n_symbols: int
        _n_permutations: int
        _n_iterations: int
        _p: int

        def __init__(self) -> None:
            self._set_defaults()

        def _set_defaults(self) -> None:
            """Initialise member variables to default values."""
            self._selected_tests = self.DEFAULT_SELECTED_TESTS
            self._n_symbols = self.DEFAULT_N_SYMBOLS
            self._n_permutations = self.DEFAULT_N_PERMUTATIONS
            self._n_iterations = self.DEFAULT_N_ITERATIONS
            self._p = self.DEFAULT_P

        @property
        def selected_tests(self) -> list[int]:
            return self._selected_tests

        @property
        def n_symbols(self) -> int:
            return self._n_symbols

        @property
        def n_permutations(self) -> int:
            return self._n_permutations

        @property
        def n_iterations(self) -> int:
            return self._n_iterations

        @property
        def p(self) -> int:
            return self._p

    def __init__(self, args: argparse.Namespace) -> None:
        """Construct a Config object from the passed command line arguments.

        Parameters
        ----------
        args : argparse.Namespace
            The application command line arguments
        """
        self._set_defaults()

        self._nist = Config.NISTConfig()
        self._stat = Config.StatConfig()

        self._apply_conf(args.config)

        self._apply_args(args)

        self._validate()

    def _set_defaults(self) -> None:
        """Initialise member variables to default values."""
        self._input_file = ""
        self._input_file_digest = ""
        self._config_file = ""
        self._config_file_read = False
        self._nist_test = self.DEFAULT_NIST_TEST
        self._statistical_analysis = self.DEFAULT_STATISTICAL_ANALYSIS
        self._min_entropy = self.DEFAULT_MINIMUM_ENTROPY
        self._parallel = self.DEFAULT_PARALLEL
        self._debug = self.DEFAULT_DEBUG

    def _read_conf(self, file: str | None) -> dict[str, typing.Any]:
        """Read a TOML configuration file into a dictionary.

        If no file is provided, read the default configuration file if it exists.
        If the default configuration file does not exist, return an empty dictionary.

        If the selected configuration file (provided or default) cannot be read, log an error and return and empty
        dictionary.

        Parameters
        ----------
        file : str | None
            the configuration file

        Returns
        -------
        dict[str, typing.Any]
            the dictionary of configuration values read from file
        """
        if file is None:
            if os.path.isfile(self.DEFAULT_CONFIG_FILE):
                file = self.DEFAULT_CONFIG_FILE
            else:
                return {}
        file = os.path.abspath(file)
        self._config_file = file

        d = {}
        try:
            with open(file, "rb") as f:
                d = tomllib.load(f)
            self._config_file_read = True
        except IOError as e:
            logger.error("Unable to open or read config file: %s", e)
        except Exception as e:
            logger.error("Unable to parse config file: %s", e)
        return d

    def _apply_conf(self, file: str | None) -> None:
        """Update the Config object with values from a configuration file.

        Parameters
        ----------
        file : str | None
            the configuration file
        """
        conf = self._read_conf(file)
        # Short-circuit if no config values to apply
        if not conf:
            return

        # Global section
        if "global" in conf:
            if "input_file" in conf["global"]:
                input_file = conf["global"]["input_file"]
                if (not isinstance(input_file, str)) or (not input_file.endswith((".bin", ".BIN", ".dat", ".DAT"))):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "global",
                        "input_file",
                        "binary file",
                    )

                input_file = os.path.abspath(os.path.expanduser(input_file))
                if not os.path.isfile(input_file):
                    logger.error("%s: %s is not a valid file: %s", self._config_file, "input_file", input_file)

                self._input_file = input_file

            if "nist_test" in conf["global"]:
                nist_test = conf["global"]["nist_test"]
                if not isinstance(nist_test, bool):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "global",
                        "nist_test",
                        "bool",
                    )

                self._nist_test = nist_test

            if "stat_analysis" in conf["global"]:
                statistical_analysis = conf["global"]["stat_analysis"]
                if not isinstance(statistical_analysis, bool):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "global",
                        "stat_analysis",
                        "bool",
                    )

                self._statistical_analysis = statistical_analysis

            if "min_entropy" in conf["global"]:
                min_entropy = conf["global"]["min_entropy"]
                if not isinstance(min_entropy, bool):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "global",
                        "min_entropy",
                        "bool",
                    )
                self._min_entropy = min_entropy

            if "parallel" in conf["global"]:
                parallel = conf["global"]["parallel"]
                if not isinstance(parallel, bool):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "global",
                        "parallel",
                        "bool",
                    )

                self._parallel = parallel

            if "debug" in conf["global"]:
                debug = conf["global"]["debug"]
                if not isinstance(debug, bool):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "global",
                        "debug",
                        "bool",
                    )

                self._debug = debug

        # nist_test section
        if "nist_test" in conf:
            if "selected_tests" in conf["nist_test"]:
                nist_selected_tests = conf["nist_test"]["selected_tests"]
                if (not isinstance(nist_selected_tests, list)) or (
                    not all(isinstance(i, int) for i in nist_selected_tests)
                ):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "nist_test",
                        "selected_tests",
                        "list of integers",
                    )

                self.nist._selected_tests = nist_selected_tests

            if "n_symbols" in conf["nist_test"]:
                nist_n_symbols = conf["nist_test"]["n_symbols"]
                if not isinstance(nist_n_symbols, int):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "nist_test",
                        "n_symbols",
                        "int",
                    )

                if nist_n_symbols < self.DEFAULT_ALPHABET_SIZE:
                    logger.error(
                        "%s: %s: invalid configuration value %s (expected >= %s)",
                        self._config_file,
                        "nist_test",
                        "n_symbols",
                        self.DEFAULT_ALPHABET_SIZE,
                    )

                self.nist._n_symbols = nist_n_symbols

            if "n_permutations" in conf["nist_test"]:
                nist_n_permutations = conf["nist_test"]["n_permutations"]
                if not isinstance(nist_n_permutations, int):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "nist_test",
                        "n_permutations",
                        "int",
                    )

                self.nist._n_permutations = nist_n_permutations

            if "first_seq" in conf["nist_test"]:
                nist_first_seq = conf["nist_test"]["first_seq"]
                if not isinstance(nist_first_seq, bool):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "nist_test",
                        "first_seq",
                        "bool",
                    )

                self.nist._first_seq = nist_first_seq

            if "plot" in conf["nist_test"]:
                nist_plot = conf["nist_test"]["plot"]
                if not isinstance(nist_plot, bool):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "nist_test",
                        "plot",
                        "bool",
                    )

                self.nist._plot = nist_plot

            if "p" in conf["nist_test"]:
                nist_p = conf["nist_test"]["p"]
                if (not isinstance(nist_p, list)) or (not all(isinstance(i, int) for i in nist_p)):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "nist_test",
                        "p",
                        "list of integers",
                    )
                elif (any(i <= 0 for i in nist_p)) or (any(i >= self.nist.n_symbols for i in nist_p)):
                    logger.error(
                        "%s: %s: parameter %s out of range (0 < %s < n_symbols)",
                        self._config_file,
                        "nist_test",
                        "p",
                        "p",
                    )

                self.nist._p = nist_p

        # statistical_analysis section
        if "statistical_analysis" in conf:
            if "selected_tests" in conf["statistical_analysis"]:
                stat_selected_tests = conf["statistical_analysis"]["selected_tests"]
                if (not isinstance(stat_selected_tests, list)) or (
                    not all(isinstance(i, int) for i in stat_selected_tests)
                ):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "statistical_analysis",
                        "selected_tests",
                        "list of integers",
                    )

                self.stat._selected_tests = stat_selected_tests

            if "n_permutations" in conf["statistical_analysis"]:
                stat_n_permutations = conf["statistical_analysis"]["n_permutations"]
                if not isinstance(stat_n_permutations, int):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "statistical_analysis",
                        "n_permutations",
                        "int",
                    )

                self.stat._n_permutations = stat_n_permutations

            if "n_symbols" in conf["statistical_analysis"]:
                stat_n_symbols = conf["statistical_analysis"]["n_symbols"]
                if not isinstance(stat_n_symbols, int):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "statistical_analysis",
                        "n_symbols",
                        "int",
                    )

                if stat_n_symbols < self.DEFAULT_ALPHABET_SIZE:
                    logger.error(
                        "%s: %s: invalid configuration value %s (expected >= %s)",
                        self._config_file,
                        "statistical_analysis",
                        "n_symbols",
                        self.DEFAULT_ALPHABET_SIZE,
                    )

                self.stat._n_symbols = stat_n_symbols

            if "n_iterations" in conf["statistical_analysis"]:
                stat_n_iterations = conf["statistical_analysis"]["n_iterations"]
                if not isinstance(stat_n_iterations, int):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "statistical_analysis",
                        "n_iterations",
                        "int",
                    )

                self.stat._n_iterations = stat_n_iterations

            if "p" in conf["statistical_analysis"]:
                stat_p = conf["statistical_analysis"]["p"]
                if not isinstance(stat_p, int):
                    logger.error(
                        "%s: %s: invalid configuration parameter %s (expected %s)",
                        self._config_file,
                        "statistical_analysis",
                        "p",
                        "int",
                    )
                elif (stat_p <= 0) or (stat_p >= self.stat.n_symbols):
                    logger.error(
                        "%s: %s: parameter %s out of range (0 < %s < n_symbols)",
                        self._config_file,
                        "statistical_analysis",
                        "p",
                        "p",
                    )

                self.stat._p = stat_p

    def _apply_args(self, args: argparse.Namespace) -> None:
        """Update the Config object with the supplied command-line arguments.

        Parameters
        ----------
        args : argparse.Namespace
            the list of arguments
        """
        # Global
        if args.input_file:
            self._input_file = os.path.abspath(os.path.expanduser(args.input_file))
        if args.nist_test is not None:
            self._nist_test = args.nist_test
        if args.stat_analysis is not None:
            self._statistical_analysis = args.stat_analysis
        if args.min_entropy is not None:
            self._min_entropy = args.min_entropy
        if args.parallel is not None:
            self._parallel = args.parallel
        if args.debug is not None:
            self._debug = args.debug
        # NIST IID tests
        if args.nist_selected_tests:
            self.nist._selected_tests = args.nist_selected_tests
        if args.nist_n_symbols:
            self.nist._n_symbols = args.nist_n_symbols
        if args.nist_n_permutations:
            self.nist._n_permutations = args.nist_n_permutations
        if args.first_seq is not None:
            self.nist._first_seq = args.first_seq
        if args.plot is not None:
            self.nist._plot = args.plot
        if args.nist_p:
            self.nist._p = args.nist_p
        # Statistical analysis
        if args.stat_selected_tests:
            self.stat._selected_tests = args.stat_selected_tests
        if args.stat_n_permutations:
            self.stat._n_permutations = args.stat_n_permutations
        if args.stat_n_symbols:
            self.stat._n_symbols = args.stat_n_symbols
        if args.stat_n_iterations:
            self.stat._n_iterations = args.stat_n_iterations
        if args.stat_p is not None:
            self.stat._p = args.stat_p

    def _validate(self) -> None:
        """Validate parameters.

        Check that required parameters are present.
        Check type and sanity of parameter values."""
        # Global
        # An input file is required
        if (
            (not isinstance(self._input_file, str))
            or (not self._input_file)
            or (not self._input_file.endswith((".bin", ".BIN", ".dat", ".DAT")))
            or (not os.path.isfile(self._input_file))
        ):
            raise ValueError(f'Invalid or missing configuration parameter: "input_file" ({self._input_file})')

        # Store the input file digest
        with open(self._input_file, "rb") as f:
            self._input_file_digest = hashlib.file_digest(f, self.DEFAULT_HASH_ALGORITHM).hexdigest()

        if not isinstance(self._nist_test, bool):
            raise ValueError(f'Invalid configuration parameter: "nist_test" ({self._nist_test})')

        if not isinstance(self._statistical_analysis, bool):
            raise ValueError(f'Invalid configuration parameter: "stat_analysis" ({self._statistical_analysis})')

        if not isinstance(self._min_entropy, bool):
            raise ValueError(f'Invalid configuration parameter: "min_entropy" ({self._min_entropy})')

        if not isinstance(self._parallel, bool):
            raise ValueError(f'Invalid configuration parameter: "parallel" ({self._parallel})')

        if not isinstance(self._debug, bool):
            raise ValueError(f'Invalid configuration parameter: "debug" ({self._debug})')

        # NIST IID tests
        if (
            (not isinstance(self.nist._selected_tests, list))
            or (not self.nist._selected_tests)
            or (not all(isinstance(i, int) for i in self.nist._selected_tests))
        ):
            raise ValueError(f'Invalid configuration parameter: "nist_selected_tests" ({self.nist._selected_tests})')
        else:
            self.nist._selected_tests = sorted(set(self.nist._selected_tests))

        if not all(i in [test.id for test in permutation_tests.tests] for i in self.nist._selected_tests):
            raise ValueError(f'Invalid test ID in "nist_selected_tests": {self.nist._selected_tests}')

        if (not self.nist._n_symbols) or (not isinstance(self.nist._n_symbols, int)):
            raise ValueError(f'Invalid configuration parameter: "nist_n_symbols" ({self.nist._n_symbols})')

        if self.nist._n_symbols < self.DEFAULT_ALPHABET_SIZE:
            raise ValueError(
                f'Invalid value for "nist_n_symbols" (must be >= {self.DEFAULT_ALPHABET_SIZE}): {self.nist._n_symbols}'
            )

        if (not self.nist._n_permutations) or (not isinstance(self.nist._n_permutations, int)):
            raise ValueError(f'Invalid configuration parameter: "nist_n_permutations" ({self.nist._n_permutations})')

        if not isinstance(self.nist._first_seq, bool):
            raise ValueError(f'Invalid configuration parameter: "first_seq" ({self.nist._first_seq})')

        if not isinstance(self.nist._plot, bool):
            raise ValueError(f'Invalid configuration parameter: "plot" ({self.nist._plot})')

        if (
            (not self.nist._p)
            or (not isinstance(self.nist._p, list))
            or (not all(isinstance(i, int) for i in self.nist._p))
        ):
            raise ValueError(f'Invalid configuration parameter: "nist_p" ({self.nist._p})')

        if (any(i <= 0 for i in self.nist._p)) or (any(i >= self.nist.n_symbols for i in self.nist._p)):
            raise ValueError(f'Parameter out of range (0 < nist_p < nist_n_symbols): "nist_p" ({self.nist._p})')

        # Statistical analysis
        if (
            (not isinstance(self.stat._selected_tests, list))
            or (not self.stat._selected_tests)
            or (not all(isinstance(i, int) for i in self.stat._selected_tests))
        ):
            raise ValueError(f'Invalid configuration parameter: "stat_selected_tests" ({self.stat._selected_tests})')
        else:
            self.stat._selected_tests = sorted(set(self.stat._selected_tests))

        if not all(i in [test.id for test in permutation_tests.tests] for i in self.stat._selected_tests):
            raise ValueError(f'Invalid test ID in "stat_selected_tests": {self.stat._selected_tests}')

        if (not self.stat._n_permutations) or (not isinstance(self.stat._n_permutations, int)):
            raise ValueError(f'Invalid configuration parameter: "stat_n_permutations" ({self.stat._n_permutations})')

        if (not self.stat._n_symbols) or (not isinstance(self.stat._n_symbols, int)):
            raise ValueError(f'Invalid configuration parameter: "stat_n_symbols" ({self.stat._n_symbols})')

        if self.stat._n_symbols < self.DEFAULT_ALPHABET_SIZE:
            raise ValueError(
                f'Invalid value for "stat_n_symbols" (must be >= {self.DEFAULT_ALPHABET_SIZE}): {self.stat._n_symbols}'
            )

        if (not self.stat._n_iterations) or (not isinstance(self.stat._n_iterations, int)):
            raise ValueError(f'Invalid configuration parameter: "n_iterations" ({self.stat._n_iterations})')

        if (not self.stat._p) or (not isinstance(self.stat._p, int)):
            raise ValueError(f'Invalid configuration parameter: "stat_p" ({self.stat._p})')

        if (self.stat._p <= 0) or (self.stat._p >= self.stat.n_symbols):
            raise ValueError(f'Parameter out of range (0 < stat_p < stat_n_symbols): "stat_p" ({self.stat._p})')

    @property
    def nist(self) -> NISTConfig:
        return self._nist

    @property
    def stat(self) -> StatConfig:
        return self._stat

    @property
    def input_file(self) -> str:
        return self._input_file

    @property
    def input_file_digest(self) -> str:
        return self._input_file_digest

    @property
    def config_file(self) -> str:
        return self._config_file

    @property
    def config_file_read(self) -> bool:
        return self._config_file_read

    @property
    def nist_test(self) -> bool:
        return self._nist_test

    @property
    def statistical_analysis(self) -> bool:
        return self._statistical_analysis

    @property
    def min_entropy(self) -> bool:
        return self._min_entropy

    @property
    def parallel(self) -> bool:
        return self._parallel

    @property
    def debug(self) -> bool:
        return self._debug

    def to_json(self) -> str:
        data = collections.OrderedDict()
        data["input_file"] = self._input_file
        data["input_file_digest"] = self._input_file_digest
        if self.config_file_read:
            data["config_file"] = self.config_file
        data["nist_test"] = self.nist_test
        data["statistical_analysis"] = self.statistical_analysis
        data["min_entropy"] = self.min_entropy
        data["parallel"] = self.parallel
        if self.nist_test:
            data["nist"] = collections.OrderedDict()
            data["nist"]["selected_tests"] = self.nist.selected_tests
            data["nist"]["n_symbols"] = self.nist.n_symbols
            data["nist"]["n_permutations"] = self.nist.n_permutations
            data["nist"]["first_seq"] = self.nist.first_seq
            data["nist"]["plot"] = self.nist.plot
            data["nist"]["p"] = self.nist.p
        if self.statistical_analysis:
            data["stat"] = collections.OrderedDict()
            data["stat"]["selected_tests"] = self.stat.selected_tests
            data["stat"]["n_symbols"] = self.stat.n_symbols
            data["stat"]["n_permutations"] = self.stat.n_permutations
            data["stat"]["n_iterations"] = self.stat.n_iterations
            data["stat"]["p"] = self.stat.p
        return json.dumps(data, ensure_ascii=False, indent=4)

    def to_json_file(self, file) -> None:
        with open(file, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    def dump(self) -> str:
        """Prints configuration in a user-readable format.

        Returns
        -------
        str
            user-readable configuration dump
        """
        if self.nist_test:
            selected_tests = ", ".join([permutation_tests.tests[i].name for i in self.nist.selected_tests])
            selected_tests_all = "all" if len(self.nist.selected_tests) == len(permutation_tests.tests) else "subset"
            nist_str = f"""n_symbols: {self.nist.n_symbols}
n_permutations: {self.nist.n_permutations}
selected tests ({selected_tests_all}): {selected_tests}
reference sequence read from {"beginning" if self.nist.first_seq else "end"} of the file
p parameter ({"NIST" if self.nist.p == self.nist.DEFAULT_P else "custom"}): {self.nist.p}"""
        else:
            nist_str = "NIST test disabled"

        if self.statistical_analysis:
            selected_tests = ", ".join([permutation_tests.tests[i].name for i in self.stat.selected_tests])
            selected_tests_all = "all" if len(self.stat.selected_tests) == len(permutation_tests.tests) else "subset"
            stat_str = f"""n_symbols: {self.stat.n_symbols}
n_permutations: {self.stat.n_permutations}
n_iterations: {self.stat.n_iterations}
selected tests ({selected_tests_all}): {selected_tests}
p parameter ({"default" if self.stat.p == self.stat.DEFAULT_P else "custom"}): {self.stat.p}"""
        else:
            stat_str = "Statistical analysis disabled"

        mine_str = f"Min-entropy calculation {'enabled' if self.min_entropy else 'disabled'}"

        return f"""Configuration info
Config file{" (invalid)" if self.config_file and not self.config_file_read else ""}: {self.config_file}
Input file ({os.path.getsize(self.input_file)}B): {self.input_file}
Input file digest ({Config.DEFAULT_HASH_ALGORITHM}): {self.input_file_digest}

NIST test parameters:
{nist_str}

Statistical analysis parameters:
{stat_str}

Min-entropy parameters:
{mine_str}
"""
