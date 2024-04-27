import os
import time
from datetime import datetime

import numpy as np
import pandas as pd

import permutation_tests
import utils.config


def save_counters(
    conf: utils.config.Config, c0: list[int], c1: list[int], elapsed_time: float, shuffle_type: str, f: str
):
    """Saves counters values obtained in the statistical analysis

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    c0 : list of int
        counter C0
    c1 : list of int
        counter C1
    elapsed_time : float
        time to execute a test
    shuffle_type : str
        type of shuffle selected
    f : str
        path to csv file
    """
    header = [
        "n_iterations_c",
        "n_symbols",
        "n_sequences",
        "shuffle",
        "test",
        "COUNTER_0",
        "COUNTER_1",
        "PROCESS_TIME",
        "DATE",
    ]
    elapsed = time.strftime("%H:%M:%S.{}".format(str(elapsed_time % 1)[2:])[:11], time.gmtime(elapsed_time))
    data = [
        conf.stat.n_iterations_c,
        conf.stat.n_symbols,
        conf.stat.n_sequences,
        shuffle_type,
        permutation_tests.tests[conf.stat.distribution_test_index].name,
        c0,
        c1,
        str(elapsed),
        str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
    ]

    # Convert the dictionary to a DataFrame and export it to a csv file
    df = pd.DataFrame(data, index=header).T

    h = not os.path.exists(f)
    df.to_csv(f, mode="a", header=h, index=False)


def save_IID_validation(conf: utils.config.Config, C0: list[int], C1: list[int], b: bool, test_time: float):
    """Saves IID failure and the counters values generated in the NIST test part

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    C0 : list of int
        counter C0
    C1 : list of int
        counter C1
    b : bool
        IID assumption
    test_time : float
        total process time
    """
    header = ["n_symbols", "n_sequences", "test_list", "COUNTER_0", "COUNTER_1", "IID", "process_time", "date"]
    d = [
        conf.nist.n_symbols,
        conf.nist.n_sequences,
        [permutation_tests.tests[i].name for i in conf.nist.selected_tests],
        C0,
        C1,
        b,
        test_time,
        str(datetime.now()),
    ]
    dt = pd.DataFrame(d, index=header).T
    # Check if the directory exists
    os.makedirs("IID_validation", exist_ok=True)
    f = os.path.join("IID_validation", "IID_validation.csv")
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
    if conf.nist.pvalues == conf.nist.DEFAULT_PVALUES:
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
    elif len(conf.nist.pvalues) == 1:
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
