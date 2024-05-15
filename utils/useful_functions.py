import csv
import logging
import os
import pathlib
from datetime import datetime

import permutation_tests
import utils.config

# Configure per-module logger
logger = logging.getLogger(f"IID_validation.{pathlib.Path(__file__).stem}")


def _save_data_helper(file: str, headers: list[str], data: list[list]) -> None:
    """Save headers and data to the specified file.

    If the file does not exist, it will be created, the headers will be written at the top, and the data appended.
    If the file exists, only the data will be appended without rewriting the headers.

    Args:
        file (str): The file path where the data has to be saved.
        headers (list[str]): The list header strings to write on top of the file.
        data (list[list]): The list of data rows to save in the file. Each row should be a list of values.
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
    dir_path: str,
):
    """Saves the outcome on the IID assumption and the counters values in a specified directory

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
    os.makedirs(dir_path, exist_ok=True)
    f = os.path.join(dir_path, "counter_values.csv")
    _save_data_helper(f, header, [d])


def save_test_values(conf: utils.config.Config, Tx, Ti):
    """Saves Tx test values and Ti test values in a csv file

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    Tx : list of float
        Tx test values calculated on one sequence
    Ti : list of float
        Ti test values calculated on the shuffled sequences
    """
    if conf.nist.p == conf.nist.DEFAULT_P:
        header = [
            "excursion_test",
            "n_directional_runs",
            "l_directional_runs",
            "n_median_runs",
            "l_median_runs",
            "n_increases_decreases",
            "avg_collision",
            "max_collision",
            "periodicity_p0",
            "periodicity_p1",
            "periodicity_p2",
            "periodicity_p3",
            "periodicity_p4",
            "covariance_p0",
            "covariance_p1",
            "covariance_p2",
            "covariance_p3",
            "covariance_p4",
            "compression",
        ]
    elif len(conf.nist.p) == 1:
        header = [permutation_tests.tests[i].name for i in conf.nist.selected_tests]
    else:
        raise Exception("Support for arbitrary p values not implemented yet")

    file_path = os.path.join("results", "save_test_values.csv")
    _save_data_helper(file_path, header, [Tx, Ti])
