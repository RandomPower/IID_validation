import os
from datetime import datetime

import numpy as np
import pandas as pd

import permutation_tests
import utils.config


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
    dt = pd.DataFrame(d, index=header).T
    # Check if the directory exists
    os.makedirs(dir_path, exist_ok=True)
    f = os.path.join(dir_path, "counter_values.csv")
    h = not os.path.exists(f)
    dt.to_csv(f, mode="a", header=h, index=False)


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

    df2 = pd.DataFrame(np.array(Ti), columns=header)
    a = pd.DataFrame([Tx], columns=header)
    df = pd.concat([a, df2]).reset_index(drop=True)
    # df.insert("time Ti", tf, True)
    file_path = os.path.join("results", "save_test_values.csv")
    write_header = not os.path.isfile(file_path)

    # Save the DataFrame to CSV, without the index and with headers only if writing for the first time
    df.to_csv(file_path, mode="a", header=write_header, index=False)
