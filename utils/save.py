import collections
import csv
import json
import logging
import os
import pathlib
import struct
from datetime import datetime

import permutation_tests

# Configure per-module logger
logger = logging.getLogger(f"IID_validation.{pathlib.Path(__file__).stem}")


def _save_data_helper(file: str, headers: list[str], data: list[list]) -> None:
    """Save headers and data to the specified file.

    If the file does not exist, it will be created, the headers will be written at the top, and the data appended.
    If the file exists, only the data will be appended without rewriting the headers.

    Parameters
    ----------
    file : str
        The file path where the data has to be saved
    headers : list of str
        The list header strings to write on top of the file
    data : list of list
        The list of data rows to save in the file. Each row should be a list of values
    """
    try:
        file_exists = os.path.exists(file)
        with open(file, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(headers)
            for d in data:
                writer.writerow(d)
    except IOError as e:
        logger.error("Unable to create or write to file (%s): %s", file, e)
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)


def save_counters(
    n_symbols: int,
    n_permutations: int,
    selected_tests: list[int],
    C0: list[int],
    C1: list[int],
    b: bool,
    test_time: float,
    dir_path: str = "",
) -> None:
    """Saves the outcome on the IID assumption and the counters values in a specified directory.

    Parameters
    ----------
    n_symbols : int
        number of symbols
    n_permutations : int
        number of permutations
    selected_tests: list of int
        the indexes of the selected tests
    C0 : list of int
        counter C0
    C1 : list of int
        counter C1
    b : bool
        IID assumption
    test_time : float
        total process time
    dir_path: str
        path of the directory
    """
    header = ["n_symbols", "n_permutations", "test_list", "COUNTER_0", "COUNTER_1", "IID", "process_time", "date"]
    d = [
        n_symbols,
        n_permutations,
        [permutation_tests.tests[i].name for i in selected_tests],
        C0,
        C1,
        b,
        test_time,
        str(datetime.now()),
    ]
    # Check if the directory exists
    f = "counter_values.csv"
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
        f = os.path.join(dir_path, f)
    _save_data_helper(f, header, [d])


def save_entropy(
    file: str, symbols_occurrences: dict, n_symbols: int, H_min: float, H_min_sigma: float, H_min_NIST: float
):
    """Saves the min-entropy for the input file

    Parameters
    ----------
    file : string
        input file
    symbols_occurrences : dict
        occurrences of symbols
    n_symbols: int
        total number of symbols
    H_min: float
        min-entropy for symbols
    H_min_sigma: float
        min-entropy for symbols
    H_min_NIST: float
        min-entropy for symbols as per NIST documentation
    """
    header = [
        "file",
        "symbols_occurrences",
        "n_symbols" "H_min_symbol",
        "H_min_symbol_sigma",
        "H_min_NIST_symbol",
        "date",
    ]
    d = [
        file,
        symbols_occurrences,
        n_symbols,
        H_min,
        H_min_sigma,
        H_min_NIST,
        str(datetime.now()),
    ]
    _save_data_helper("min_entropy_values.csv", header, [d])


class TestResults:
    """A helper class to interact with test results."""

    class Binary:
        """The binary representation of a test result."""

        # Header
        # unsigned int : length of Ti
        # unsigned int : bitmask of selected tests
        # unsigned char: number of p parameters
        _header_fmt = "=IIB"
        _header_size = struct.calcsize(_header_fmt)

        @staticmethod
        def header_format_size() -> tuple[str, int]:
            """Return the format string and size of the header.

            Returns
            -------
            tuple[str, int]
                The format string and size in bytes of the test result header.
            """
            return __class__._header_fmt, __class__._header_size

        @staticmethod
        def p_format_size(len_p: int) -> tuple[str, int]:
            """Return the format string and size of p.

            Parameters
            ----------
            len_p : int
                The length of p

            Returns
            -------
            tuple[str, int]
                The format string and size in bytes of p.
            """
            p_fmt = "=" + "I" * len_p
            p_size = struct.calcsize(p_fmt)
            return p_fmt, p_size

        @staticmethod
        def entry_format_size(selected_tests: list[int], p: list[int]) -> tuple[str, int]:
            """Compute the format string and size of an entry.

            Parameters
            ----------
            selected_tests : list[int]
                The selected tests in the test result entry
            p : list[int]
                The lag parameters p used to obtain the test result entry

            Returns
            -------
            tuple[str, int]
                The format string and size in bytes of the test result entry.
            """
            # Build a test result entry depending on the selected tests
            #        double      : excursion result
            #        unsigned int: n_directional_runs result
            #        unsigned int: l_directional_runs result
            #        unsigned int: n_increases_decreases result
            #        unsigned int: n_median_runs result
            #        unsigned int: l_median_runs result
            #        double      : avg_collision result
            #        unsigned int: max_collision result
            # len(p) unsigned int: periodicity results for each p
            # len(p) unsigned int: covariance results for each p
            #        unsigned int: compression result
            entry_fmt = "="
            if permutation_tests.excursion.id in selected_tests:
                entry_fmt += "d"
            if permutation_tests.n_directional_runs.id in selected_tests:
                entry_fmt += "I"
            if permutation_tests.l_directional_runs.id in selected_tests:
                entry_fmt += "I"
            if permutation_tests.n_increases_decreases.id in selected_tests:
                entry_fmt += "I"
            if permutation_tests.n_median_runs.id in selected_tests:
                entry_fmt += "I"
            if permutation_tests.l_median_runs.id in selected_tests:
                entry_fmt += "I"
            if permutation_tests.avg_collision.id in selected_tests:
                entry_fmt += "d"
            if permutation_tests.max_collision.id in selected_tests:
                entry_fmt += "I"
            if permutation_tests.periodicity.id in selected_tests:
                entry_fmt += "I" * len(p)
            if permutation_tests.covariance.id in selected_tests:
                entry_fmt += "I" * len(p)
            if permutation_tests.compression.id in selected_tests:
                entry_fmt += "I"

            entry_size = struct.calcsize(entry_fmt)
            return entry_fmt, entry_size

    @staticmethod
    def encode_selected_tests_bitmask(selected_tests: list[int]) -> int:
        """Encode the list of selected test indexes into a bitmask. Selected tests are represented by a 1.

        Parameters
        ----------
        selected_tests : list[int]
            The list of test indexes selected from the available ones

        Returns
        -------
        int
            An integer containing the resulting bitmask
        """
        bitmask = 0
        for i in range(len(permutation_tests.tests)):
            if i in selected_tests:
                bitmask += 1 << i
        return bitmask

    @staticmethod
    def decode_selected_tests_bitmask(bitmask: int) -> list[int]:
        """Decode a bitmask into a list of selected test indexes.

        Parameters
        ----------
        bitmask : int
            An integer containing the selected tests bitmask

        Returns
        -------
        list[int]
            The list of selected test indexes decoded from the bitmask
        """
        selected_tests = []
        for i in range(len(permutation_tests.tests)):
            if bitmask & 1:
                selected_tests.append(i)
            bitmask >>= 1
        return selected_tests

    @staticmethod
    def to_bytes(selected_tests: list[int], Tx: list[float], Ti: list[list[float]], p: list[int]) -> bytes:
        """Pack test results into a compact binary representation.

        Parameters
        ----------
        selected_tests : list[int]
            The list of selected test indexes
        Tx : list[float]
            The list of reference test results corresponding to the selected tests
        Ti : list[list[float]]
            A list of test result lists, each containing the selected test results
        p : list[int]
            The lag parameter p

        Returns
        -------
        bytes
            The output byte string
        """
        offset = 0
        # Prepare the output buffer
        header_fmt, header_size = __class__.Binary.header_format_size()
        p_fmt, p_size = __class__.Binary.p_format_size(len(p))
        entry_fmt, entry_size = __class__.Binary.entry_format_size(selected_tests, p)
        # Header + Tx + Ti
        b = bytearray(header_size + p_size + entry_size + (len(Ti) * entry_size))
        # Write the header
        selected_tests_bitmask = __class__.encode_selected_tests_bitmask(selected_tests)
        struct.pack_into(header_fmt, b, offset, len(Ti), selected_tests_bitmask, len(p))
        offset += header_size
        # Write p
        struct.pack_into(p_fmt, b, offset, *p)
        offset += p_size
        # Write Tx
        struct.pack_into(entry_fmt, b, offset, *Tx)
        offset += entry_size
        # Write Ti
        for t in Ti:
            struct.pack_into(entry_fmt, b, offset, *t)
            offset += entry_size
        return bytes(b)

    @staticmethod
    def to_binary_file(
        file: str, selected_tests: list[int], Tx: list[float], Ti: list[list[float]], p: list[int]
    ) -> None:
        """Write test results to a binary file.

        Parameters
        ----------
        file : str
            The output file name
        selected_tests : list[int]
            The list of selected test indexes
        Tx : list[float]
            The list of reference test results corresponding to the selected tests
        Ti : list[list[float]]
            A list of test result lists, each containing the selected test results
        p : list[int]
            The lag parameter p
        """
        with open(file, mode="wb") as f:
            f.write(__class__.to_bytes(selected_tests, Tx, Ti, p))

    @staticmethod
    def from_bytes(b: bytes) -> tuple[list[int], list[float], list[list[float]], list[int]]:
        """Read test results from a compact binary representation.

        Parameters
        ----------
        b : bytes
            The input byte string

        Returns
        -------
        tuple[list[int], list[float], list[list[float]], list[int]]
            selected_tests : list[int]
                The list of selected test indexes
            Tx : list[float]
                The list of reference test results corresponding to the selected tests
            Ti : list[list[float]]
                A list of test result lists, each containing the selected test results
            p : list[int]
                The lag parameter p
        """
        offset = 0
        # Read the header
        header_fmt, header_size = __class__.Binary.header_format_size()
        len_Ti, selected_tests_bitmask, len_p = struct.unpack_from(header_fmt, b, offset)
        offset += header_size
        selected_tests = __class__.decode_selected_tests_bitmask(selected_tests_bitmask)
        # Read p
        p_fmt, p_size = __class__.Binary.p_format_size(len_p)
        p: list[int] = list(struct.unpack_from(p_fmt, b, offset))
        offset += p_size
        # Read Tx
        entry_fmt, entry_size = __class__.Binary.entry_format_size(selected_tests, p)
        Tx: list[float] = list(struct.unpack_from(entry_fmt, b, offset))
        offset += entry_size
        # Read Ti
        Ti = []
        for i in range(len_Ti):
            t: list[float] = list(struct.unpack_from(entry_fmt, b, offset))
            offset += entry_size
            Ti.append(t)
        return selected_tests, Tx, Ti, p

    @staticmethod
    def from_binary_file(file: str) -> tuple[list[int], list[float], list[list[float]], list[int]]:
        """Read test results from a binary file.

        Parameters
        ----------
        file : str
            The input binary file

        Returns
        -------
        tuple[list[int], list[float], list[list[float]], list[int]]
            selected_tests : list[int]
                The list of selected test indexes
            Tx : list[float]
                The list of reference test results corresponding to the selected tests
            Ti : list[list[float]]
                A list of test result lists, each containing the selected test results
            p : list[int]
                The lag parameter p
        """
        with open(file, mode="rb") as f:
            return __class__.from_bytes(f.read())

    @staticmethod
    def test_labels(selected_tests: list[int], p: list[int]) -> list[str]:
        """Generate labels corresponding to selected tests and p

        Parameters
        ----------
        selected_tests : list[int]
            A list of selected tests
        p : list[int]
            A list of parameters p

        Returns
        -------
        list[str]
            A list of labels, one for each test, with optional p variants
        """
        labels = []
        if permutation_tests.excursion.id in selected_tests:
            labels.append(permutation_tests.excursion.name)
        if permutation_tests.n_directional_runs.id in selected_tests:
            labels.append(permutation_tests.n_directional_runs.name)
        if permutation_tests.l_directional_runs.id in selected_tests:
            labels.append(permutation_tests.l_directional_runs.name)
        if permutation_tests.n_increases_decreases.id in selected_tests:
            labels.append(permutation_tests.n_increases_decreases.name)
        if permutation_tests.n_median_runs.id in selected_tests:
            labels.append(permutation_tests.n_median_runs.name)
        if permutation_tests.l_median_runs.id in selected_tests:
            labels.append(permutation_tests.l_median_runs.name)
        if permutation_tests.avg_collision.id in selected_tests:
            labels.append(permutation_tests.avg_collision.name)
        if permutation_tests.max_collision.id in selected_tests:
            labels.append(permutation_tests.max_collision.name)
        if permutation_tests.periodicity.id in selected_tests:
            labels.extend([f"{permutation_tests.periodicity.name}{n}" for n in p])
        if permutation_tests.covariance.id in selected_tests:
            labels.extend([f"{permutation_tests.covariance.name}{n}" for n in p])
        if permutation_tests.compression.id in selected_tests:
            labels.append(permutation_tests.compression.name)
        return labels

    @staticmethod
    def to_json(selected_tests: list[int], Tx: list[float], Ti: list[list[float]], p: list[int]) -> str:
        """Dump test results to JSON.

        Parameters
        ----------
        selected_tests : list[int]
            The list of selected test indexes
        Tx : list[float]
            The list of reference test results corresponding to the selected tests
        Ti : list[list[float]]
            A list of test result lists, each containing the selected test results
        p : list[int]
            The lag parameter p

        Returns
        -------
        str
            The output JSON string
        """
        data = collections.OrderedDict()
        data["p"] = p
        data["selected_tests"] = __class__.test_labels(selected_tests, p)
        data["Tx"] = Tx
        data["Ti"] = Ti

        return json.dumps(data, ensure_ascii=False, indent=4)

    @staticmethod
    def to_json_file(
        file: str, selected_tests: list[int], Tx: list[float], Ti: list[list[float]], p: list[int]
    ) -> None:
        """Dump test results to a JSON file.

        Parameters
        ----------
        file : str
            The output file name
        selected_tests : list[int]
            The list of selected test indexes
        Tx : list[float]
            The list of reference test results corresponding to the selected tests
        Ti : list[list[float]]
            A list of test result lists, each containing the selected test results
        p : list[int]
            The lag parameter p
        """
        with open(file, "w", encoding="utf-8") as f:
            f.write(__class__.to_json(selected_tests, Tx, Ti, p))

    @staticmethod
    def to_csv_file(
        file: str, selected_tests: list[int], Tx: list[float], Ti: list[list[float]], p: list[int]
    ) -> None:
        """Dump test results to a CSV file.

        Parameters
        ----------
        file : str
            The output file name
        selected_tests : list[int]
            The list of selected test indexes
        Tx : list[float]
            The list of reference test results corresponding to the selected tests
        Ti : list[list[float]]
            A list of test result lists, each containing the selected test results
        p : list[int]
            The lag parameter p
        """
        headers = __class__.test_labels(selected_tests, p)
        _save_data_helper(file, headers, [Tx, *Ti])
